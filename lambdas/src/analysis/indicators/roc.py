import ta

# Rate of Change
#gucci
def run(params, candles, timeframe):
    roc = ta.momentum.roc(close = candles["c"], n = 12, fillna = False)
    print(' Rate of Change: ', roc)


    signals = []
    last_signal = "hold"
    for i in range(1, len(roc)):
        curr_roc = roc.iloc[i]
        next_roc = roc.iloc[i+1]

        base_transaction = {
            'indicator': 'roc',
            'price': float(candles['c'][i]),
            'time': int(candles['t'][i]),
            'tf': timeframe,
            'str': 100
        }

        # to avoid out of bounds
        if i+1 == len(roc) - 1:
            break

        #if we go from negative to positive indicates bullish trend so buy
        elif curr_roc > 0 and next_roc < 0 and last_signal != "buy":
            last_signal = "buy"
            base_transaction["sig"] = last_signal
            signals.append(base_transaction)
        #if we our roc is positive and goes to negative then indicates bearish trend so sell
        elif curr_roc < 0 and next_roc > 0 and last_signal != "sell":
            last_signal = "sell"
            base_transaction["sig"] = last_signal
            signals.append(base_transaction)

    print("printing Rate of Change signals")
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
