import streamlit as st
import requests
import pandas as pd
import numpy as np

API_URL = st.secrets.get("API_URL", "http://localhost:8000")

st.title("🎯 Optimización del Envío de Flota")

@st.fragment
def render_optimizador():
    c_ocioso = st.slider("Costo de Taxi Ocioso/Hora ($)", 5, 50, 10)
    c_perdido = st.slider("Costo de Pasajero Perdido ($)", 10, 100, 40)
    
    cuantil_opt = c_perdido / (c_perdido + c_ocioso)
    st.latex(r"\text{Cuantil Óptimo} = \frac{C_{\text{perdido}}}{C_{\text{perdido}} + C_{\text{ocioso}}} = " + f"{cuantil_opt:.2f}")
    
    q_target = f"p{int(round(cuantil_opt, 1) * 100)}"
    st.info(f"💡 Estrategia Sugerida: Se recomienda cubrir la demanda usando la predicción del cuantil **{q_target}**.")
    
    try:
        r = requests.get(f"{API_URL}/pronostico", params={"zona_id": 161, "fecha": "2024-01-25"}).json()
        df_dec = pd.DataFrame([{**h["cuantiles"], "hora": h["hora"], "real": h["real"]} for h in r["horas"]])
        df_dec["taxis_recomendados"] = df_dec[q_target]
        
        if df_dec["real"].notnull().all():
            df_dec["costo_estrategia"] = np.maximum(df_dec["taxis_recomendados"] - df_dec["real"], 0) * c_ocioso + \
                                         np.maximum(df_dec["real"] - df_dec["taxis_recomendados"], 0) * c_perdido
            st.metric("Costo Financiero Total Estimado", f"${df_dec['costo_estrategia'].sum():,.2f}")
            
        st.download_button(
            "📥 Descargar Plan Operacional de Taxis (CSV)",
            df_dec[["hora", "taxis_recomendados"]].to_csv(index=False),
            "plan_taxis.csv",
            "text/csv"
        )
    except Exception as e:
        st.warning(f"Conéctate a la API para ver la simulación financiera en tiempo real. Error: {e}")

render_optimizador()
