import ta
import pandas as pd

# Awesome Oscillator
# lil off but solid
def run(candles, timeframe, params=None):
    ao = ta.momentum.awesome_oscillator(
        high=candles["high"], low=candles["low"], window1=5, window2=34, fillna=True
    )

    candles = candles.assign(ao=ao.values)
    signals = pd.DataFrame(columns=["unix", "signal"])

    last_signal = trend = None

    for index, row in candles.iterrows():
        if len(candles) == index + 1:
            break

        curr_ao = row["ao"]
        next_ao = candles["ao"][index + 1]
        curr_price = row["close"]
        # out of bounds
        if index < 2:
            continue

        prev_ao = candles["ao"][index - 1]
        # if we are in uptrend
        if curr_ao > 0 and (
            curr_ao < prev_ao and next_ao < curr_ao and last_signal != "sell"
        ):
            # two down candles in a row means dying trend
            last_signal = "sell"
            signals = signals.append(
                {"unix": row["unix"], "signal": last_signal, "indicator": "ao"},
                ignore_index=True,
            )
            continue

        if curr_ao < 0 and (
            curr_ao > prev_ao and next_ao > curr_ao and last_signal != "buy"
        ):
            # two down candles in a row means dying trend
            last_signal = "buy"
            signals = signals.append(
                {"unix": row["unix"], "signal": last_signal, "indicator": "ao"},
                ignore_index=True,
            )

    return signals[signals["signal"].notna()]
