from fastapi import FastAPI, HTTPException, Query
from datetime import date
import pandas as pd
import numpy as np
import xgboost as xgb
import json

app = FastAPI(title="API de Pronostico de Taxis NYC")

# Carga de datos y modelo
demanda_df = pd.read_parquet("demanda.parquet")
demanda_df["PULocationID"] = demanda_df["PULocationID"].astype("category")

with open("info_modelo.json", "r", encoding="utf-8") as f:
    info_modelo = json.load(f)

modelo = xgb.XGBRegressor()
modelo.load_model("modelo_pronostico.ubj")

VARIABLES = ["PULocationID", "hora", "dia_semana", "es_feriado", "lag_24", "lag_48", "lag_168"]

@app.get("/")
def home():
    return {"status": "ok", "message": "API en linea"}

@app.get("/info")
def get_info():
    zonas_list = []
    for z_id in info_modelo["zonas"]:
        zonas_list.append({
            "id": z_id,
            "nombre": info_modelo["nombres_zonas"].get(str(z_id), "Zona NYC"),
            "distrito": info_modelo["distritos_zonas"].get(str(z_id), "NYC")
        })
    return {
        "zonas": zonas_list,
        "fechas_disponibles": ["2024-01-25", "2024-01-26", "2024-01-27", "2024-01-28", "2024-01-29", "2024-01-30", "2024-01-31", "2024-02-01"],
        "cuantiles": ["p10", "p20", "p30", "p40", "p50", "p60", "p70", "p80", "p90"]
    }

@app.get("/pronostico")
def get_pronostico(zona_id: int = Query(...), fecha: date = Query(...)):
    filas = demanda_df[(demanda_df["PULocationID"] == zona_id) & (demanda_df["fecha_hora"].dt.date == fecha)].copy()
    if filas.empty:
        raise HTTPException(status_code=404, detail="No hay datos para esa zona o fecha")

    filas = filas.sort_values("hora")
    preds = modelo.predict(filas[VARIABLES])
    preds_sorted = np.sort(preds, axis=1)

    resultado_horas = []
    for idx, (_, row) in enumerate(filas.iterrows()):
        q_dict = {f"p{(i+1)*10}": round(float(preds_sorted[idx, i]), 1) for i in range(9)}
        val_real = float(row["viajes"]) if pd.notnull(row["viajes"]) and fecha < date(2024, 2, 1) else None
        val_lag168 = float(row["lag_168"]) if pd.notnull(row["lag_168"]) else None

        resultado_horas.append({
            "hora": int(row["hora"]),
            "real": val_real,
            "hace_una_semana": val_lag168,
            "cuantiles": q_dict
        })

    return {
        "zona": {
            "id": zona_id,
            "nombre": info_modelo["nombres_zonas"].get(str(zona_id), "Zona NYC"),
            "distrito": info_modelo["distritos_zonas"].get(str(zona_id), "NYC")
        },
        "fecha": str(fecha),
        "horas": resultado_horas
    }
