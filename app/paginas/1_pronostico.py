import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime, date

st.title("📈 Pronóstico de Demanda de Taxis en NYC")
st.markdown("Consulta las predicciones de demanda por zona y fecha utilizando el modelo de Machine Learning con cuantiles.")

# URL de tu API en Render (cámbiala por la tuya cuando la despliegues, o usa datos locales de respaldo)
API_URL = st.secrets.get("API_URL", "https://tu-api-en-render.onrender.com")

@st.cache_data
def obtener_info_api():
    try:
        response = requests.get(f"{API_URL}/info", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    # Respaldo local si la API aún no está arriba en Render
    return {
        "zonas": [{"id": 7, "nombre": "Astoria", "distrito": "Queens"}, {"id": 132, "nombre": "JFK Airport", "distrito": "Queens"}],
        "fechas_disponibles": ["2024-01-25", "2024-01-26", "2024-01-27", "2024-01-28", "2024-01-29", "2024-01-30", "2024-01-31", "2024-02-01"]
    }

info = obtener_info_api()
zonas_opciones = {f"{z['nombre']} (ID: {z['id']})": z['id'] for z in info.get("zonas", [])}

st.sidebar.subheader("Parámetros de Consulta")
zona_seleccionada_str = st.sidebar.selectbox("Selecciona la Zona de Origen:", list(zonas_opciones.keys()) if zonas_opciones else ["Zona (ID: 7)"])
zona_id = zonas_opciones.get(zona_seleccionada_str, 7)

fechas_disp = [datetime.strptime(f, "%Y-%m-%d").date() for f in info.get("fechas_disponibles", ["2024-01-25"])]
fecha_seleccionada = st.sidebar.date_input("Selecciona la Fecha:", value=fechas_disp[0], min_value=min(fechas_disp), max_value=max(fechas_disp))

if st.sidebar.button("Generar Pronóstico"):
    with st.spinner("Consultando la API de pronóstico..."):
        try:
            res = requests.get(f"{API_URL}/pronostico", params={"zona_id": zona_id, "fecha": str(fecha_seleccionada)}, timeout=10)
            if res.status_code == 200:
                data = res.json()
                df_res = pd.DataFrame(data["horas"])
                
                st.subheader(f"Resultados para {zona_seleccionada_str} el {fecha_seleccionada}")
                
                # Gráfico con Plotly y banda de incertidumbre (p10 - p90)
                fig = go.Figure()
                
                # Banda de incertidumbre p10 a p90
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
                    mode='lines+markers', name='Mediana Pronosticada (p50)', line=dict(color='blue', width=2)
                ))
                
                # Valor Real (si existe)
                if "real" in df_res.columns and df_res["real"].notnull().any():
                    fig.add_trace(go.Scatter(
                        x=df_res["hora"], y=df_res["real"],
                        mode='lines+markers', name='Valor Real', line=dict(color='green', dash='dash', width=2)
                    ))

                # Igual que hace una semana (lag_168)
                if "hace_una_semana" in df_res.columns and df_res["hace_una_semana"].notnull().any():
                    fig.add_trace(go.Scatter(
                        x=df_res["hora"], y=df_res["hace_una_semana"],
                        mode='lines', name='Igual hace una semana', line=dict(color='orange', width=1)
                    ))

                fig.update_layout(xaxis_title="Hora del Día", yaxis_title="Número de Viajes", template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
                
                st.metric(label="Demanda Mediana Total Esperada (Día)", value=int(df_res["cuantiles"].apply(lambda x: x.get("p50")).sum()))
            else:
                st.error("La API no devolvió datos para los parámetros seleccionados.")
        except Exception as e:
            st.error(f"No se pudo conectar con la API en Render: {e}[cite: 14]. Asegúrate de que la API esté desplegada correctamente.")
else:
    st.info("Selecciona una zona y fecha en la barra lateral y presiona **Generar Pronóstico**.")
