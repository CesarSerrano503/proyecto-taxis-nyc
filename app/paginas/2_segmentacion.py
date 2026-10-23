import streamlit as st
import pandas as pd
import plotly.express as px

st.title("🧩 Segmentación de Zonas de NYC")

df_seg = pd.read_csv("app/data/zonas_segmentadas.csv")

grupos = list(df_seg["nombre_grupo"].unique())
grupo_sel = st.pills("Filtrar por Grupos", grupos, selection_mode="multi", default=grupos)

df_filt = df_seg[df_seg["nombre_grupo"].isin(grupo_sel)]

fig = px.scatter(
    df_filt, x="pca_1", y="pca_2", color="nombre_grupo",
    hover_data=["nombre_zona", "distrito", "viajes_dia"],
    title="Mapa Bidimensional PCA de Zonas",
    labels={"pca_1": "Componente Principal 1", "pca_2": "Componente Principal 2"}
)

st.plotly_chart(fig, on_select="rerun", use_container_width=True)

st.subheader("Detalle por Zona")
st.dataframe(
    df_filt[["nombre_zona", "distrito", "nombre_grupo", "viajes_dia", "distancia_mediana", "tarifa_mediana"]],
    column_config={
        "viajes_dia": st.column_config.ProgressColumn("Promedio Viajes/Día", format="%.0f", min_value=0, max_value=5000),
        "distancia_mediana": st.column_config.NumberColumn("Distancia (mi)", format="%.1f mi"),
        "tarifa_mediana": st.column_config.NumberColumn("Tarifa Mediana", format="$%.2f")
    },
    use_container_width=True
)
