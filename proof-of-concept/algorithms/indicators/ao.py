import ta

# Awesome Oscillator
# lil off but solid
def run(params, candles, timeframe):
    ao = ta.momentum.ao(high = candles["h"], low = candles["l"], s = 5, len = 34, fillna = False)
    print('Awesome Oscillator: ', ao)
    signals = []
    last_signal = "flat"
    trend = "flat"

    for i in range(len(ao)):
        curr_ao = ao.iloc[i]
        next_ao = ao.iloc[i+1]
        curr_price = candles["c"][i]
        #out of bounds
        if i+1 == len(ao)-1:
            break;
        elif i >= 2:
        #if we are in uptrend
            if curr_ao > 0:
                # two down candles in a row means dying trend
                if curr_ao < ao.iloc[i-1] and next_ao < curr_ao and last_signal != "sell":
                    last_signal = "sell"
                    signals.append({
                    'indicator': 'ao',
                    'sig': 'sell',
                    'price': float(candles['c'][i]),
                    'time': int(candles['t'][i]),
                    'tf': timeframe,
                    'str': 100
                    })

            elif curr_ao < 0:
                # two down candles in a row means dying trend
                if curr_ao > ao.iloc[i-1] and next_ao > curr_ao and last_signal != "buy":
                    last_signal = "buy"
                    signals.append({
                    'indicator': 'ao',
                    'sig': 'buy',
                    'price': float(candles['c'][i]),
                    'time': int(candles['t'][i]),
                    'tf': timeframe,
                    'str': 100
                    })

    print("printing AwesomeOscillator signals")
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
