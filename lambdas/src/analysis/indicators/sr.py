import ta
from decimal import Decimal

# Stochastic Oscillator
def run(params, candles, timeframe):
    all_sr = ta.momentum.StochasticOscillator(high = candles["h"], low = candles["l"], close = candles["c"], n = 14, d_n = 3, fillna = False)
    sr_sig = all_sr.stoch_signal()
    print('sr_sig: ', sr_sig)

    last_signal = 'hold'
    signals = []
    
    for i in range(0, len(all_sr.stoch_signal())):
        curr_sr = all_sr.stoch_signal().iloc[i]
        base_transaction = {
            'indicator': 'sr',
            'price': float(candles['c'][i]),
            'time': int(candles['t'][i]),
            'tf': timeframe,
            'str': round(Decimal((100 - curr_sr - 10) / 100), 10)
        }
        if (curr_sr < 100) and (curr_sr > 0):
            if (curr_sr < params['buy'] and last_signal != 'buy'):
                last_signal = 'buy'
                base_transaction["sig"] = last_signal
                signals.append(base_transaction)
            elif (curr_sr > params['sell'] and last_signal != 'sell'):
                last_signal = 'sell'
                base_transaction["sig"] = last_signal
                signals.append(base_transaction)

    print("printing StochOscillator signals")
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
