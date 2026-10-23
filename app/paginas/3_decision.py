import streamlit as st
import pandas as pd

st.title("🛡️ Optimización de Flota y Decisión Económica")
st.markdown("Calcula cuántos taxis enviar por hora basándote en la asimetría de costos operativos y pérdida de ingresos.")

col1, col2 = st.columns(2)
with col1:
    costo_ocioso = st.number_input("Costo de taxi ocioso (1 hora sin pasajero):", min_value=1.0, value=10.0, step=1.0)
with col2:
    costo_perdido = st.number_input("Costo por pasajero sin servicio (pérdida de viaje):", min_value=1.0, value=40.0, step=1.0)

# Fórmula del cuantil óptimo (Newsvendor model)
cuantil_optimo_val = costo_perdido / (costo_perdido + costo_ocioso)
p_sugerido_idx = int(round(cuantil_optimo_val * 10) * 10)
p_sugerido_idx = max(10, min(90, p_sugerido_idx))

st.success(f"### Cuantil Óptimo Calculado: **p{p_sugerido_idx}** (Ratio: {cuantil_optimo_val:.2f})")

st.markdown(f"""
* **Interpretación:** Dado que un pasajero sin servicio cuesta **${costo_perdido}** frente a los **${costo_ocioso}** de tener un auto ocioso, la estrategia óptima recomienda cubrir la demanda hasta el nivel del percentil **p{p_sugerido_idx}** para maximizar la rentabilidad y minimizar la insatisfacción.
""")
