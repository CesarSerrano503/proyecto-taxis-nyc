import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

API_URL = st.secrets.get("API_URL", "http://localhost:8000")

@st.cache_data(ttl=3600)
def obtener_info_api():
    r = requests.get(f"{API_URL}/info", timeout=90)
    return r.json()

@st.cache_data(ttl=3600)
def obtener_pronostico(zona_id, fecha_str):
    r = requests.get(f"{API_URL}/pronostico", params={"zona_id": zona_id, "fecha": fecha_str}, timeout=90)
    return r.json()

@st.dialog("¿Cómo leer este pronóstico?")
def abrir_ayuda():
    st.write("""
    - **Línea central (p50):** Es la estimación de la mediana del pronóstico.
    - **Banda sombreada (p10-p90):** Representa el rango de incertidumbre del 80%.
    - **Puntos verdes:** Viajes reales observados en la semana de prueba.
    """)

st.title("📈 Pronóstico de Demanda por Hora")

if st.button("ℹ️ Cómo leerlo"):
    abrir_ayuda()

try:
    info = obtener_info_api()
    zonas_dict = {f"{z['nombre']} ({z['distrito']})": z['id'] for z in info['zonas']}
    
    col1, col2 = st.columns(2)
    with col1:
        zona_sel = st.selectbox("Selecciona la Zona", list(zonas_dict.keys()))
        zona_id = zonas_dict[zona_sel]
    with col2:
        fecha_sel = st.selectbox("Fecha de Análisis", info["fechas_disponibles"])
        
    datos = obtener_pronostico(zona_id, str(fecha_sel))
    df_res = pd.DataFrame([{
        "hora": h["hora"],
        "real": h["real"],
        "hace_una_semana": h["hace_una_semana"],
        **h["cuantiles"]
    } for h in datos["horas"]])
    
    # Métricas clave
    m1, m2, m3 = st.columns(3)
    m1.metric("Viajes Esperados (p50)", f"{df_res['p50'].sum():,.0f}")
    m2.metric("Hora Pico", f"{df_res.loc[df_res['p50'].idxmax(), 'hora']}:00 hrs")
    m3.metric("Rango del Día (p10-p90)", f"{df_res['p10'].sum():,.0f} - {df_res['p90'].sum():,.0f}")
    
    # Gráfico Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_res["hora"], y=df_res["p90"], mode='lines', line=dict(width=0), showlegend=False))
    fig.add_trace(go.Scatter(x=df_res["hora"], y=df_res["p10"], mode='lines', line=dict(width=0), fill='tonexty', fillcolor='rgba(0,100,80,0.2)', name='Banda (p10-p90)'))
    fig.add_trace(go.Scatter(x=df_res["hora"], y=df_res["p50"], mode='lines+markers', name='Pronóstico Mediana (p50)', line=dict(color='black', width=3)))
    
    if fecha_sel != "2024-02-01" and df_res["real"].notnull().any():
        fig.add_trace(go.Scatter(x=df_res["hora"], y=df_res["real"], mode='markers', name='Demanda Real', marker=dict(color='red', size=8)))
        
    st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.error(f"⚠️ No se pudo conectar con la API en {API_URL}. Detalles: {e}")
