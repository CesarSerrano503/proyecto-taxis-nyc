import streamlit as st

st.title("📋 Ficha del Modelo y Consideraciones Éticas")
st.markdown("Documentación técnica y marco ético del proyecto de pronóstico de demanda de taxis en Nueva York.")

st.subheader("🔍 Resumen Técnico del Modelo")
st.markdown("""
- **Algoritmo Principal:** XGBoost Regressor optimizado para predicción basada en cuantiles.
- **Variables de Entrada:** Historial de viajes, hora del día, día de la semana, indicadores de días feriados y retardos temporales (*lags* de 24, 48 y 168 horas).
- **Métricas de Evaluación:** Error Absoluto Medio (MAE) y cobertura de cuantiles.
""")

st.subheader("⚖️ Consideraciones Éticas y Sesgos")
st.markdown("""
- **Equidad Territorial:** El modelo prioriza zonas con mayor volumen histórico, por lo que se implementaron filtros de segmentación para asegurar visibilidad en distritos con menor densidad de viajes.
- **Privacidad de los Datos:** Todos los registros de viajes utilizados provienen de fuentes públicas anonimizadas de la Comisión de Taxis y Limusinas de NYC (TLC).
- **Uso Responsable:** Las recomendaciones de asignación de flota son orientativas y buscan optimizar tiempos de espera sin afectar las condiciones laborales de los conductores.
""")

st.markdown("---")
st.caption("Desarrollado para el proyecto final de Machine Learning aplicado (AIMLF1).")
