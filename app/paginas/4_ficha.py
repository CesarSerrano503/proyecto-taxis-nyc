import streamlit as st

st.title("📋 Ficha del Modelo y Uso Responsable")

st.markdown("""
### 📌 Propósito y Alcance
Este modelo pronostica la demanda horaria de taxis amarillos en las principales zonas de Nueva York para planificar la flota con 24 horas de anticipación.

### 📊 Desempeño y Cobertura
- **Cobertura del Intervalo [p10-p90]:** ~82% de los datos reales caen dentro del rango predicho.
- **Comparación con Basales:** El modelo supera a la regla simple de "igual que hace una semana", aportando un **valor estratégico clave al proporcionar el rango de incertidumbre**.

### ⚠️ Limitaciones Conocidas
1. **Factor Climático y Eventos:** No incorpora datos de clima en tiempo real, accidentes o cierres viales.
2. **Estacionalidad:** Fue entrenado exclusivamente con un mes de invierno (Enero 2024).

### 🚫 Usos No Recomendados
- **Evaluación de Conductores:** No debe utilizarse para penalizar o medir el rendimiento individual de un chofer.
- **Recorte de Servicio Periférico:** No se debe justificar el retiro de servicio en barrios periféricos basándose únicamente en baja demanda de taxis amarillos.
""")

rating = st.feedback("stars")
if rating is not None:
    st.toast(f"¡Gracias por evaluar esta ficha técnica! Valoración: {rating + 1}/5 estrellas.")
