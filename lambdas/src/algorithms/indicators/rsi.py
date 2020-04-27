import ta

# Relative Strength Index
def run(params, candles, timeframe):
    rsi_total = ta.momentum.rsi(close = candles["c"], n = 14, fillna = True)

    signals = []
    last_signal = 'hold'

    for i in range(len(rsi_total)):
        current_rsi = rsi_total.iloc[i]
        if (current_rsi < 100) and (current_rsi > 0):
            if (current_rsi < params['buy'] and last_signal != 'buy'):
                last_signal = 'buy'
                signals.append({
                    'indicator': 'rsi',
                    'sig': 'buy',
                    'price': float(candles['c'][i]),
                    'time': int(candles['t'][i]),
                    'tf': timeframe,
                    'str': round(Decimal((100 - current_rsi - 10) / 100), 10)
                })
            elif (current_rsi > params['sell'] and last_signal != 'sell'):
                last_signal = 'sell'
                signals.append({
                    'indicator': 'rsi',
                    'sig': 'sell',
                    'price': float(candles['c'][i]),
                    'time': int(candles['t'][i]),
                    'tf': timeframe,
                    'str': round(Decimal((current_rsi - 10) / 100), 10)
                })

    for i in range(len(signals)):
        print(signals[i])

    return signals