import ta

# Mass Index, we are using psar to get trend
# good
def run(params, candles, timeframe):
    all_psar = ta.trend.PSARIndicator(high = candles["h"], low = candles["l"], close = candles["c"], step = 0.02, max_step = 0.2, fillna = False)
    psar = all_psar.psar()
    mi = ta.trend.mass_index(high = candles["h"], low = candles["l"], n = 10, n2 = 10, fillna = False)
    print('Mass Index: ', mi)
    signals = []
    trend = "flat"
    last_signal = "hold"

    for i in range(len(mi)):
        curr_mi = mi.iloc[i]
        next_mi = mi.iloc[i+1]
        curr_price = candles["c"][i]
        current_psar = psar.iloc[i]

        #to avoid out of bounds error
        if i+1 == len(mi)-1:
            break

        # when the mass index is over 27 we are very likely to see a reversal in the trend
        # or we are topping out basically
        elif curr_mi > 25and current_psar > curr_price:
            if next_mi <= 24.5:
                trend = "down"
                last_signal = "sell"
                signals.append({
                'indicator': 'mi',
                'sig': 'sell',
                'price': float(candles['c'][i]),
                'time': int(candles['t'][i]),
                'tf': timeframe,
                'str': 69
                })
            # when the mass index is over 27 we are very likely to see a reversal in the trend
            # or we are bottoming out
        elif curr_mi > 25 and current_psar < curr_price:
            if next_mi <= 24.5:
                trend = "up"
                last_signal = "buy"
                signals.append({
                'indicator': 'mi',
                'sig': 'buy',
                'price': float(candles['c'][i]),
                'time': int(candles['t'][i]),
                'tf': timeframe,
                'str': 69
                })


    print("printing Mass Index signals")
    pct_change = 0
    bal = 1000
    for i in range(len(signals)):
        if i+1 == len(signals)-1:
            break
        print(signals[i])
        curr_price = signals[i]['price']
        next_price = signals[i+1]['price']
        if signals[i]['sig'] == 'buy' and signals[i+1]['sig'] == 'sell':
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

    return signals
