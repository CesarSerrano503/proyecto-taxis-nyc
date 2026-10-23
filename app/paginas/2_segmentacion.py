import streamlit as st
import pandas as pd
import os

st.title("🧩 Segmentación de Zonas de Taxi en NYC")
st.markdown("Explora los grupos o clusters en los que se dividen las zonas de Nueva York según sus patrones de viaje.")

# Cargar el archivo CSV de zonas segmentadas asegurando la ruta correcta
ruta_csv = "app/data/zonas_segmentadas.csv" # Por si acaso está dentro de la carpeta app

if os.path.exists(ruta_csv):
    df_zonas = pd.read_csv(ruta_csv)
    
    st.subheader("📊 Datos de Segmentación por Zona")
    st.dataframe(df_zonas, use_container_width=True)
    
    # Filtro opcional por cluster si existe la columna
    if "cluster" in df_zonas.columns:
        st.subheader("🔍 Filtrar Zonas por Grupo (Cluster)")
        clusters_disponibles = sorted(df_zonas["cluster"].unique())
        cluster_seleccionado = st.selectbox("Selecciona un cluster:", clusters_disponibles)
        
        df_filtrado = df_zonas[df_zonas["cluster"] == cluster_seleccionado]
        st.write(f"Mostrando zonas pertenecientes al grupo **{cluster_seleccionado}**:")
        st.dataframe(df_filtrado, use_container_width=True)
else:
    st.error("No se encontró el archivo `zonas_segmentadas.csv` en el repositorio. Por favor, asegúrate de subirlo.")
