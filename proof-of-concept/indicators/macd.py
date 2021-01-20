import ta
import pandas as pd

# Moving Average Convergence Divergence
# histogram and signal values match up, but the "macd signal one is not matching up well...
# this one represents the macd fast line on tradingview"
def run(candles, timeframe, params = None):
    macd = ta.trend.macd_diff(close = candles["close"], window_slow = 26, window_fast = 12, window_sign = 9, fillna = False)
    candles = candles.assign(macd=macd.values)
    signals = pd.DataFrame(columns = ['unix', 'signal'])

    last_signal = ""

    for index, row in candles.iterrows():
        if len(candles) == index + 1:
            break

        curr_macd = row["macd"]
        next_macd = candles["macd"][index+1]

        #if we go from negative to positive indicates bullish trend so buy
        if curr_macd < 0 and next_macd > 0 and last_signal != "buy":
            last_signal = "buy"
            signals = signals.append({'unix' : row["unix"], 'signal' : last_signal}, ignore_index=True)
            continue

        #if we our macd is positive and goes to negative then indicates bearish trend so sell
        if curr_macd > 0 and next_macd < 0 and last_signal != "sell":
            last_signal = "sell"
            signals = signals.append({'unix' : row["unix"], 'signal' : last_signal}, ignore_index=True)
            continue

    return signals[signals["signal"].notna()]
