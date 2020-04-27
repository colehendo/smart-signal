import ta

# Stochastic Oscillator
#sr_sig correlates to the %K line on tradingview
def run(params, candles, timeframe):
    all_sr = ta.momentum.StochasticOscillator(high = candles["h"], low = candles["l"], close = candles["c"], n = 14, d_n = 3, fillna = False)
    print('HERE IS Stochastic Oscillator!!!!')
    sr_sig = all_sr.stoch_signal()
    print('sr_sig: ', sr_sig)

    last_signal = 'hold'
    signals = []
    for i in range(0, len(all_sr.stoch_signal())):
        curr_sr = all_sr.stoch_signal().iloc[i]
        if (curr_sr < 100) and (curr_sr > 0):
            if (curr_sr < params['buy'] and last_signal != 'buy'):
                last_signal = 'buy'
                signals.append({
                    'indicator': 'sr',
                    'sig': 'buy',
                    'price': float(candles['c'][i]),
                    'time': int(candles['t'][i]),
                    'tf': timeframe,
                    'str': round(Decimal((100 - curr_sr - 10) / 100), 10)
                })
            elif (curr_sr > params['sell'] and last_signal != 'sell'):
                last_signal = 'sell'
                signals.append({
                    'indicator': 'sr',
                    'sig': 'sell',
                    'price': float(candles['c'][i]),
                    'time': int(candles['t'][i]),
                    'tf': timeframe,
                    'str': round(Decimal((100 - curr_sr - 10) / 100), 10)
                })

    print("printing stochOscillator signals")
    for i in range(len(signals)):
        print(signals[i])

    return signals