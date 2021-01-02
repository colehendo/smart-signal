from find_max_profit import FindMaxProfit
from shared.data import Visuals
import os

def main():
    asset_type = "cryptocurrency"
    symbol = "BTC"
    timeframe="hour"
    max_profit = FindMaxProfit(asset_type=asset_type, symbol=symbol, timeframe=timeframe).max_profit()
    print(max_profit)
    Visuals().plot()


if __name__ == "__main__":
    main()