import ta

# Average Directional Movement Index
def run(params, candles, timeframe):
    all_adx = ta.trend.ADXIndicator(high = candles["h"], low = candles["l"], close = candles["c"], n = 14, fillna = False)
    print("Average Directional Movement Index")
    adx = all_adx.adx()
    print("adx: ", adx)
    neg = all_adx.adx_neg()
    print("neg adx: ", neg)
    pos = all_adx.adx_pos()
    print("pos adx: ", pos)
    signals = []
    last_signal = "hold"

    # assuming pos and neg adx"s are same size, hopefully adx too
    for i in range(len(neg)):
        curr_adx = adx.iloc[i]
        next_adx = adx.iloc[i+1]
        curr_neg = neg.iloc[i]
        next_neg = neg.iloc[i+1]
        curr_pos = pos.iloc[i]
        next_pos = pos.iloc[i+1]
        # to avoid out of bounds error
        if i+1 == len(neg) - 1:
            break;
        # if pos > neg then we should be in a uptrend
        elif curr_pos > curr_neg and last_signal != "sell":
            if next_pos < next_neg: # we were in uptrend but now it crosses down
                if curr_adx > params["strong"]: #strong trend in down direction, stronger signal
                    last_signal = "sell"
                    signals.append({
                    "indicator": "adx",
                    "sig": "sell",
                    "price": float(candles["c"][i]),
                    "time": int(candles["t"][i]),
                    "tf": timeframe,
                    "str": 100
                    })
                else: #weaker signal strength
                    last_signal = "sell"
                    signals.append({
                    "indicator": "adx",
                    "sig": "sell",
                    "price": float(candles["c"][i]),
                    "time": int(candles["t"][i]),
                    "tf": timeframe,
                    "str": 30
                    })
        # should be in downtrend if pos < neg
        elif curr_pos < curr_neg and last_signal != "buy":
            if next_pos > next_neg: # we were in downtrend but now it crosses up
                if curr_adx > params["strong"]:
                    last_signal = "buy"
                    signals.append({
                    "indicator": "adx",
                    "sig": "buy",
                    "price": float(candles["c"][i]),
                    "time": int(candles["t"][i]),
                    "tf": timeframe,
                    "str": 100
                    })
                else: #weaker signal strength
                    last_signal = "buy"
                    signals.append({
                    "indicator": "adx",
                    "sig": "buy",
                    "price": float(candles["c"][i]),
                    "time": int(candles["t"][i]),
                    "tf": timeframe,
                    "str": 30
                    })

    print("printing ADX signals")
    pct_change = 0
    bal = 1000
    for i in range(len(signals)):
        if i+1 == len(signals)-1:
            break
        print(signals[i])
        curr_price = signals[i]["price"]
        next_price = signals[i+1]["price"]
        if signals[i]["sig"] == "buy" and signals[i+1]["sig"] == "sell":
            print("curr price: ", curr_price)
            print("next price: ", next_price)
            diff =  ((next_price - curr_price) / curr_price)
            print("diff: ", diff)
            bal = bal + (bal * diff)
            print("bal: ", bal)
            pct_change = pct_change + diff
            print("pct_change: ", pct_change)


    myroi = round((((bal - 1000) / 1000) * 100), 2)
    print("Total roi is: ", myroi, "%")
    gain = round((bal - 1000), 2)
    print("Total gain is: $", gain)
    print("Balance is: $", bal)
    print("Total pct change is: ", round((pct_change), 2))
    return signals
