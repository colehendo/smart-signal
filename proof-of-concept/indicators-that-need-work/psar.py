import ta

# Parabolic Stop And Reverse
# we'll trigger signals whenever we have a reversal so if
def run(params, candles, timeframe):
    all_psar = ta.trend.PSARIndicator(
        high=candles["h"],
        low=candles["l"],
        close=candles["c"],
        step=0.02,
        max_step=0.2,
        fillna=False,
    )
    print("Parabolic Stop And Reverse")
    psar = all_psar.psar()
    # print('psar: ', psar)
    signals = []
    trend = "flat"
    last_signal = "hold"
    ##make sure to account for last signal
    for i in range(len(psar)):
        current_psar = psar.iloc[i]
        curr_price = candles["c"][i]
        if trend == "up" and current_psar > curr_price and last_signal != "sell":
            # print("appending a sell")
            last_signal = "sell"
            signals.append(
                {
                    "indicator": "psar",
                    "sig": "sell",
                    "price": float(candles["c"][i]),
                    "time": int(candles["t"][i]),
                    "tf": timeframe,
                    "str": 100,
                }
            )
            trend = "down"
        elif trend == "down" and current_psar < curr_price and last_signal != "buy":
            # print("appending a buy")
            last_signal = "buy"
            signals.append(
                {
                    "indicator": "psar",
                    "sig": "buy",
                    "price": float(candles["c"][i]),
                    "time": int(candles["t"][i]),
                    "tf": timeframe,
                    "str": 100,
                }
            )
            trend = "up"
        else:
            if current_psar > curr_price:
                trend = "down"
            elif current_psar < curr_price:
                trend = "up"
            else:
                trend = "flat"

    return signals
