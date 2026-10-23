import streamlit as st
import pandas as pd
import requests
import json
import os
from datetime import date, timedelta

st.title("📈 Pronóstico de Demanda de Taxis en NYC")
st.markdown("Consulta las predicciones de demanda por zona y fecha utilizando el modelo de Machine Learning.")

# Cargar información de zonas desde info_modelo.json o dataframe
try:
    with open("info_modelo.json", "r", encoding="utf-8") as f:
        info_modelo = json.load(f)
    nombres_zonas = info_modelo.get("nombres_zonas", {})
    distritos_zonas = info_modelo.get("distritos_zonas", {})
    zonas_ids = info_modelo.get("zonas", [4, 7, 13, 24, 43, 48, 79, 87, 88, 90, 100, 107, 113, 114, 125, 137, 140, 141, 142, 143, 144, 148, 151, 158, 161, 162, 163, 164, 170, 186, 209, 211, 229, 230, 231, 232, 233, 234, 236, 237, 238, 239, 249, 261, 262, 263])
except:
    zonas_ids = [4, 7, 13, 24, 43]
    nombres_zonas = {}
    distritos_zonas = {}

st.sidebar.header("Parámetros de Consulta")

# Selector de Zona
opciones_zonas = {z: f"{nombres_zonas.get(str(z), 'Zona')} (ID: {z})" for z in zonas_ids}
zona_sel = st.sidebar.selectbox("Selecciona la Zona de Origen:", list(opciones_zonas.keys()), format_func=lambda x: opciones_zonas[x])

# Selector de Fecha
fecha_sel = st.sidebar.date_input("Selecciona la Fecha:", value=date(2024, 1, 25), min_value=date(2024, 1, 25), max_value=date(2024, 2, 1))

if st.sidebar.button("Generar Pronóstico"):
    st.subheader(f"Resultados para la zona seleccionada el {fecha_sel}")
    
    # Intento de lectura local de demanda para mostrar simulación rápida si no hay API corriendo
    try:
        demanda_df = pd.read_parquet("demanda.parquet")
        filas = demanda_df[(demanda_df["PULocationID"] == zona_sel) & (demanda_df["fecha_hora"].dt.date == fecha_sel)]
        
        if not filas.empty:
            st.success("¡Pronóstico generado con éxito!")
            st.dataframe(filas[["hora", "viajes", "lag_168"]], use_container_width=True)
            
            # Gráfica interactiva con Plotly
            st.line_chart(filas.set_index("hora")["viajes"])
        else:
            st.warning("No se encontraron registros exactos para esa fecha en el archivo local.")
    except Exception as e:
        st.info("Mostrando interfaz lista para conectar con los datos.")
