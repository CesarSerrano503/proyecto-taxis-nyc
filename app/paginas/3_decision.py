import streamlit as st
import pandas as pd

st.title("🎯 Optimización y Toma de Decisiones")
st.markdown("Herramienta de apoyo orientada a directivos y operadores de flotas para la distribución eficiente de unidades de taxi.")

st.subheader("💡 Recomendaciones Operativas Basadas en Cuantiles")
st.write("Utiliza los pronósticos de alta demanda (cuantiles superiores como p80 y p90) para anticipar la concentración de vehículos en zonas críticas.")

col1, col2 = st.columns(2)

with col1:
    st.info("**Horarios Pico Detectados**")
    st.write("- Mañanas (07:00 - 09:00)")
    st.write("- Tardes / Noches (17:00 - 20:00)")

with col2:
    st.success("**Estrategia Sugerida de Flota**")
    st.write("- Reasignar 20% de unidades hacia hubs de alta demanda en Manhattan y aeropuertos.")
    st.write("- Establecer incentivos dinámicos para conductores en horas de menor cobertura.")

st.markdown("---")
st.subheader("⚙️ Simulador de Asignación de Recursos")
unidades = st.slider("Número total de unidades disponibles para reasignar:", min_value=50, max_value=1000, value=200, step=50)
st.write(f"Con **{unidades} unidades**, se recomienda distribuir 60% en zonas comerciales y 40% en zonas residenciales/periféricas.")
