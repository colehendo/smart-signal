import ta
import pandas as pd

# Relative Strength Index
def run(candles, timeframe, params=None):
    rsi = ta.momentum.rsi(close=candles["close"], window=14, fillna=True)

    # buy = params["buy"] if params.get("buy") else 30
    # sell = params["sell"] if params.get("sell") else 70
    buy = 30
    sell = 70

    candles = candles.assign(rsi=rsi.values)
    signals = pd.DataFrame(columns=["unix", "signal"])

    last_signal = top = top_rsi = bottom = bottom_rsi = None

    for index, row in candles.iterrows():
        curr_rsi = row["rsi"]
        curr_price = row["close"]
        # store most extreme values
        if not top or top < curr_price:
            top = curr_price
            top_rsi = curr_rsi
        if not bottom or bottom > curr_price:
            bottom = curr_price
            bottom_rsi = curr_rsi

        if (curr_rsi > 100) or (curr_rsi < 0):
            continue

        if curr_rsi < buy and (
            last_signal != "buy" or (curr_price < bottom and curr_rsi > bottom_rsi)
        ):
            last_signal = "buy"
            signals = signals.append(
                {"unix": row["unix"], "signal": last_signal}, ignore_index=True
            )
            continue

        if curr_rsi > sell and (
            last_signal != "sell" or (curr_price < top and curr_rsi > top_rsi)
        ):
            last_signal = "sell"
            signals = signals.append(
                {"unix": row["unix"], "signal": last_signal}, ignore_index=True
            )

    return signals[signals["signal"].notna()]
