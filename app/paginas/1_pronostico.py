import streamlit as st
import pandas as pd
import numpy as np
import requests
import os
import xgboost as xgb
import plotly.graph_objects as go
from datetime import datetime

st.title("📈 Pronóstico de Demanda de Taxis en NYC")
st.markdown("Consulta las predicciones de demanda por zona y fecha utilizando el modelo de Machine Learning con cuantiles.")

API_URL = st.secrets.get("API_URL", "https://tu-api-en-render.onrender.com")

@st.cache_data
def cargar_datos_locales():
    ruta_parquet = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../app_data/demanda.parquet"))
    ruta_modelo = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../app_data/modelo_pronostico.ubj"))
    
    df_demanda = None
    modelo = None
    
    if os.path.exists(ruta_parquet):
        df_demanda = pd.read_parquet(ruta_parquet)
        df_demanda["fecha_hora"] = pd.to_datetime(df_demanda["fecha_hora"])
    
    if os.path.exists(ruta_modelo):
        modelo = xgb.XGBRegressor()
        modelo.load_model(ruta_modelo)
        
    return df_demanda, modelo

df_local, modelo_local = cargar_datos_locales()

# Obtener lista de zonas disponibles
zonas_disponibles = []
if df_local is not None:
    zonas_unicas = df_local["PULocationID"].unique()
    zonas_disponibles = [{"id": int(z), "nombre": f"Zona (ID: {z})", "distrito": "NYC"} for z in zonas_unicas]
else:
    zonas_disponibles = [{"id": 7, "nombre": "Astoria", "distrito": "Queens"}, {"id": 132, "nombre": "JFK Airport", "distrito": "Queens"}]

st.sidebar.subheader("Parámetros de Consulta")
zona_opciones_dict = {f"{z['nombre']} (ID: {z['id']})": z['id'] for z in zonas_disponibles}
zona_seleccionada_str = st.sidebar.selectbox("Selecciona la Zona de Origen:", list(zona_opciones_dict.keys()))
zona_id = zona_opciones_dict[zona_seleccionada_str]

fecha_min = datetime(2024, 1, 25).date()
fecha_max = datetime(2024, 2, 1).date()
fecha_seleccionada = st.sidebar.date_input("Selecciona la Fecha:", value=fecha_min, min_value=fecha_min, max_value=fecha_max)

if st.sidebar.button("Generar Pronóstico"):
    datos_obtenidos = None
    
    # 1. Intentar vía API
    try:
        res = requests.get(f"{API_URL}/pronostico", params={"zona_id": zona_id, "fecha": str(fecha_seleccionada)}, timeout=3)
        if res.status_code == 200:
            datos_obtenidos = res.json()["horas"]
    except:
        pass
        
    # 2. Respaldo local si la API falla
    if datos_obtenidos is None and df_local is not None and modelo_local is not None:
        filas = df_local[(df_local["PULocationID"] == zona_id) & (df_local["fecha_hora"].dt.date == fecha_seleccionada)].copy()
        if not filas.empty:
            filas = filas.sort_values("hora") if "hora" in filas.columns else filas.sort_values("fecha_hora")
            if "hora" not in filas.columns:
                filas["hora"] = filas["fecha_hora"].dt.hour
                
            VARIABLES = ["PULocationID", "hora", "dia_semana", "es_feriado", "lag_24", "lag_48", "lag_168"]
            CUANTILES = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
            
            preds = modelo_local.predict(filas[VARIABLES])
            preds_sorted = np.sort(preds, axis=1)
            
            datos_obtenidos = []
            for idx, (_, row) in enumerate(filas.iterrows()):
                q_dict = {f"p{(i+1)*10}": round(float(preds_sorted[idx, i]), 1) for i in range(9)}
                val_real = float(row["viajes"]) if "viajes" in row and pd.notnull(row["viajes"]) and fecha_seleccionada < datetime(2024, 2, 1).date() else None
                val_lag168 = float(row["lag_168"]) if "lag_168" in row and pd.notnull(row["lag_168"]) else None
                
                datos_obtenidos.append({
                    "hora": int(row["hora"]),
                    "real": val_real,
                    "hace_una_semana": val_lag168,
                    "cuantiles": q_dict
                })

    if datos_obtenidos:
        df_res = pd.DataFrame(datos_obtenidos)
        st.subheader(f"Resultados para la zona seleccionada el {fecha_seleccionada}")
        
        fig = go.Figure()
        
        # Banda de incertidumbre p10 a p90[cite: 13]
        fig.add_trace(go.Scatter(
            x=df_res["hora"], y=df_res["cuantiles"].apply(lambda x: x.get("p90")),
            mode='lines', line=dict(width=0), showlegend=False
        ))
        fig.add_trace(go.Scatter(
            x=df_res["hora"], y=df_res["cuantiles"].apply(lambda x: x.get("p10")),
            mode='lines', line=dict(width=0), fill='tonexty',
            fillcolor='rgba(68, 68, 68, 0.2)', name='Banda de Incertidumbre [p10-p90]'
        ))
        
        # Mediana (p50)
        fig.add_trace(go.Scatter(
            x=df_res["hora"], y=df_res["cuantiles"].apply(lambda x: x.get("p50")),
            mode='lines+markers', name='Mediana Pronosticada (p50)', line=dict(color='#0068c9', width=2)
        ))
        
        # Valor real[cite: 13]
        if "real" in df_res.columns and df_res["real"].notnull().any():
            fig.add_trace(go.Scatter(
                x=df_res["hora"], y=df_res["real"],
                mode='lines+markers', name='Valor Real', line=dict(color='#21c354', dash='dash', width=2)
            ))

        fig.update_layout(xaxis_title="Hora del Día", yaxis_title="Número de Viajes", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
        
        total_mediana = int(df_res["cuantiles"].apply(lambda x: x.get("p50")).sum())
        st.metric(label="Demanda Mediana Total Esperada (Día)", value=total_mediana)
    else:
        st.error("No se encontraron registros de pronóstico para la zona y fecha seleccionadas.")
else:
    st.info("Selecciona una zona y fecha en la barra lateral y presiona **Generar Pronóstico**.")
