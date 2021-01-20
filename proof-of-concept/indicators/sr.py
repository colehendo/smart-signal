import ta
import pandas as pd

# Stochastic Oscillator
# sr_sig correlates to the %K line on tradingview
def run(candles, timeframe, params=None):
    sr = ta.momentum.stoch(
        high=candles["high"],
        low=candles["low"],
        close=candles["close"],
        window=14,
        smooth_window=3,
        fillna=True,
    )

    sell = 80
    buy = 20

    candles = candles.assign(sr=sr.values)
    signals = pd.DataFrame(columns=["unix", "signal"])

    last_signal = None

    for index, row in candles.iterrows():
        curr_sr = row["sr"]
        if (curr_sr > 100) or (curr_sr < 0):
            continue

        if curr_sr < buy and last_signal != "buy":
            last_signal = "buy"
            signals = signals.append(
                {"unix": row["unix"], "signal": last_signal}, ignore_index=True
            )
            continue

        if curr_sr > sell and last_signal != "sell":
            last_signal = "sell"
            signals = signals.append(
                {"unix": row["unix"], "signal": last_signal}, ignore_index=True
            )

    return signals[signals["signal"].notna()]
