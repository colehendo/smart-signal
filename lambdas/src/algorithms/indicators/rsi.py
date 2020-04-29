import ta
from decimal import Decimal

# Relative Strength Index
def run(params, candles, timeframe):
    rsi_total = ta.momentum.rsi(close = candles["c"], n = 14, fillna = True)

    signals = []
    last_signal = 'hold'
    top = 0
    bottom = 10000000
    top_index = 0
    bottom_index = 0

    for i in range(len(rsi_total)):
        current_rsi = rsi_total.iloc[i]
        curr_price = candles["c"][i]
        #store highest values
        if top < curr_price:
            top = curr_price
            top_index = i
        if bottom > curr_price:
            bottom = curr_price
            bottom_index = i

        if (current_rsi < 100) and (current_rsi > 0):

            if (current_rsi < params['buy']):
                if last_signal != 'buy': #general case we dont want duplicate buy signals
                    last_signal = 'buy'
                    signals.append({
                        'indicator': 'rsi',
                        'sig': 'buy',
                        'price': float(candles['c'][i]),
                        'time': int(candles['t'][i]),
                        'tf': timeframe,
                        'str': round(Decimal((100 - current_rsi - 10) / 100), 10)
                    })
                # elif last_signal == 'buy':
                #     if

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
