import streamlit as st

st.set_page_config(
    page_title="Proyecto Taxis NYC - AIMLF1",
    page_icon="🚖",
    layout="wide"
)

# Definir las páginas del menú lateral multipágina
paginas = [
    st.Page("paginas/1_pronostico.py", title="Pronóstico de Demanda", icon="📈"),
    st.Page("paginas/2_segmentacion.py", title="Segmentación de Zonas", icon="🧩"),
    st.Page("paginas/3_decision.py", title="Optimización de Flota", icon="🎯"),
    st.Page("paginas/4_ficha.py", title="Ficha del Modelo y Ética", icon="📋")
]

pg = st.navigation(paginas)
pg.run()