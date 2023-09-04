import ta

# Williams %R
#gucci
def run(params, candles, timeframe):
    all_wr = ta.momentum.wr(high = candles["h"], low = candles["l"], close = candles["c"], lbp = 14, fillna = False)
    # wr = all_wr.wr()
    print('Williams %R: ', all_wr)

    last_signal = 'hold'
    signals = []
    for i in range(0, len(all_wr)):
        curr_wr = all_wr.iloc[i]
        base_transaction = {
            'indicator': 'wr',
            'price': float(candles['c'][i]),
            'time': int(candles['t'][i]),
            'tf': timeframe,
            'str': 100
        }
        if (curr_wr > params['buy'] and last_signal != 'buy'):
            last_signal = 'buy'
            base_transaction["sig"] = last_signal
            signals.append(base_transaction)
        elif (curr_wr < params['sell'] and last_signal != 'sell'):
            last_signal = 'sell'
            base_transaction["sig"] = last_signal
            signals.append(base_transaction)

    print("printing WR% signals")
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
