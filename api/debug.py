import pandas as pd

df = pd.read_parquet("demanda.parquet")
print("Primeras filas de zonas y fechas:")
print(df[['PULocationID', 'fecha_hora']].drop_duplicates().head(20))
