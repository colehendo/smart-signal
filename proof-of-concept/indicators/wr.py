import ta
import pandas as pd

# Williams %R
# gucci
def run(candles, timeframe, params=None):
    wr = ta.momentum.williams_r(
        high=candles["high"], low=candles["low"], close=candles["close"], lbp=14, fillna=False
    )

    buy = 20
    sell = 80

    candles = candles.assign(wr=wr.values)
    signals = pd.DataFrame(columns=["unix", "signal"])

    last_signal = None

    for index, row in candles.iterrows():
        curr_wr = row["wr"]

        if curr_wr < buy and last_signal != "buy":
            last_signal = "buy"
            signals = signals.append(
                {"unix": row["unix"], "signal": last_signal}, ignore_index=True
            )
            continue

        if curr_wr > sell and last_signal != "sell":
            last_signal = "sell"
            signals = signals.append(
                {"unix": row["unix"], "signal": last_signal}, ignore_index=True
            )

    return signals[signals["signal"].notna()]
