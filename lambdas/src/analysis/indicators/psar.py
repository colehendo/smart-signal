import ta

# Parabolic Stop And Reverse
def run(params, candles, timeframe):
    all_psar = ta.trend.PSARIndicator(high = candles["h"], low = candles["l"], close = candles["c"], step = 0.02, max_step = 0.2, fillna = False)
    print('Parabolic Stop And Reverse')
    psar = all_psar.psar()
    # print('psar: ', psar)
    signals = []
    trend = "flat"
    last_signal = "hold"
    ##make sure to account for last signal
    for i in range(len(psar)):
        current_psar = psar.iloc[i]
        curr_price = candles["c"][i]
        base_transaction = {
            'indicator': 'psar',
            'price': float(candles['c'][i]),
            'time': int(candles['t'][i]),
            'tf': timeframe,
            'str': 100
        }
        if trend == "up" and current_psar > curr_price and last_signal != 'sell':
            last_signal = 'sell'
            base_transaction["sig"] = last_signal
            signals.append(base_transaction)
            trend = "down"
        elif trend == "down" and current_psar < curr_price and last_signal != 'buy':
            last_signal = 'buy'
            base_transaction["sig"] = last_signal
            signals.append(base_transaction)
            trend = "up"
        else:
            if current_psar > curr_price:
                trend = "down"
            elif current_psar < curr_price:
                trend = "up"
            else:
                trend = "flat"

    print("printing PSAR signals")
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
