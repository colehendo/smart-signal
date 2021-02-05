import ta
import pandas as pd

# Rate of Change
# gucci
def run(params, candles, timeframe):
    roc = ta.momentum.roc(close=candles["close"], window=12, fillna=True)

    candles = candles.assign(roc=roc.values)
    signals = pd.DataFrame(columns=["unix", "signal"])

    last_signal = None

    for index, row in candles.iterrows():
        if index < 1:
            continue

        curr_roc = row["roc"]
        prev_roc = candles["roc"][index - 1]

        # if we go from negative to positive indicates bullish trend so buy
        if curr_roc > 0 and prev_roc < 0 and last_signal != "buy":
            last_signal = "buy"
            signals = signals.append(
                {"unix": row["unix"], "signal": last_signal, "indicator": "roc"},
                ignore_index=True,
            )
            continue

        # if we our roc is positive and goes to negative then indicates bearish trend so sell
        if curr_roc < 0 and prev_roc > 0 and last_signal != "sell":
            last_signal = "sell"
            signals = signals.append(
                {"unix": row["unix"], "signal": last_signal, "indicator": "roc"},
                ignore_index=True,
            )

    return signals[signals["signal"].notna()]
