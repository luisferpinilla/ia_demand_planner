# -*- coding: utf-8 -*-
"""
Created on Sun Feb  9 11:49:25 2025

@author: luisf
"""
import pandas as pd
from prophet import Prophet
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import os
from prophet.serialize import model_to_json, model_from_json


class Forecaster:

    def __init__(self, history_df: pd.DataFrame):

        self.history_df = history_df
        self.models = dict()

    def forecast_sku(self, sku) -> pd.DataFrame:

        ts = (
            self.history_df[[sku]]
            .reset_index()
            .rename(columns={"Fecha": "ds", sku: "y"})
        )

        cap = ts["y"].max() * 2

        ts["cap"] = cap
        ts["floor"] = 0

        m = Prophet(growth="logistic")
        m.fit(ts)

        self.models[sku] = m

        future = m.make_future_dataframe(periods=36, freq="ME")
        future["cap"] = cap
        future["floor"] = 0
        forecast = m.predict(future)
        forecast["ds"] = pd.to_datetime(forecast["ds"]).dt.strftime("%Y-%m-%d")
        forecast["sku"] = sku

        ts["ds"] = pd.to_datetime(ts["ds"]).dt.strftime("%Y-%m-%d")

        forecast = pd.merge(
            left=forecast,
            right=ts.rename(columns={"y": "history"}),
            left_on="ds",
            right_on="ds",
            how="left",
        )

        return forecast

    def run(self):

        workers_count = os.cpu_count() - 1

        with ThreadPoolExecutor(max_workers=workers_count) as executor:
            results = list(
                tqdm(
                    executor.map(self.forecast_sku, self.history_df.columns[1:]),
                    total=len(self.history_df.columns[1:]),
                )
            )

        self.forecast_df = pd.concat(results)

    def save_models(self, file_path: str):

        models = dict()
        for sku, model in self.models.items():
            models[sku] = model_to_json(model)

        with open(file_path, "w") as writer:
            writer.write(models)

    def save_forecast(self):
        self.forecast_df.to_parquet("forecast.parquet")

    def get_forecast(self) -> pd.DataFrame:
        return self.forecast_df

    def get_models(self) -> dict:
        return self.models
