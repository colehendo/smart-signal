from importlib import import_module
from pandas import DataFrame


class RunIndicators:
    @staticmethod
    def get_indicator_values(
        candles: DataFrame,
        indicator_name: str,
    ) -> DataFrame:
        return import_module("indicators." + indicator_name).get_values(
            candles=candles, indicator_name=indicator_name
        )

    @staticmethod
    def run_indicator_analysis(
        indicator_name: str,
        results: DataFrame = None,
    ):
        return import_module("indicators." + indicator_name).analyze(
            data=results, indicator_name=indicator_name
        )
