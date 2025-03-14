# -*- coding: utf-8 -*-
"""
Created on Sun Feb  9 11:48:43 2025

@author: luisf
"""

import pandas as pd
import calendar
from datetime import datetime
from tqdm import tqdm


from forecaster import Forecaster

dtypes = {
    "Planta": str,
    "IdCliente": str,
    "IdProducto": str,
    "Año": str,
    "Mes": str,
    "Periodo": str,
    "UnidadesVendidas": str,
    "DolaresVendidos": str,
    "PesosVendidos": str,
    "PrecioVentaUSD": str,
    "PrecioVentaCOP": str,
}

df = pd.read_csv("../../data/Ventas.txt", dtype=dtypes)

# Remover signos $ de las columnas de dinero
columnas_dinero = [
    "DolaresVendidos",
    "PesosVendidos",
    "PrecioVentaUSD",
    "PrecioVentaCOP",
]
columnas_cantidad = ["Año", "Mes", "Periodo", "UnidadesVendidas"]

for columna in tqdm(columnas_dinero):
    df[columna] = df[columna].apply(lambda x: float(x.replace("$", "")))

for columna in tqdm(columnas_cantidad):
    df[columna] = df[columna].apply(lambda x: int(x))

df["dia"] = df.apply(lambda row: calendar.monthrange(row["Año"], row["Mes"])[1], axis=1)

df["Fecha"] = df.apply(lambda x: datetime(x["Año"], x["Mes"], x["dia"]).date(), axis=1)


history_df = df.pivot_table(
    values="UnidadesVendidas", index="Fecha", columns="IdProducto", aggfunc="sum"
).fillna(0)

# Remover columnas cuya suma sea 0  
sku_sin_ventas = history_df.columns[history_df.sum() == 0]
history_df.drop(columns=sku_sin_ventas, inplace=True)

forecaster = Forecaster(history_df)

forecaster.run()

forecast_df = forecaster.get_forecast()

forecaster.save_models("models.json")

print("Escribiendo archivo parquet")
forecaster.save_forecast()
print("Archivo parquet escrito")
