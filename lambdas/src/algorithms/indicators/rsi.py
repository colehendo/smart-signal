import ta
from decimal import Decimal

# Relative Strength Index
def run(params, candles, timeframe):
    rsi_total = ta.momentum.rsi(close = candles["c"], n = 14, fillna = True)

    signals = []
    last_signal = 'hold'
    top = 0
    bottom = 10000000
    top_index, bottom_index = 0

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
                elif last_signal == 'buy':
                    # if our current price is less than the current bottom,
                    # but we have a higher rsi (rsi double bottom signal)
                    if curr_price < bottom and current_rsi > rsi_total.iloc[bottom_index]:
                        last_signal = 'buy'
                        signals.append({
                            'indicator': 'rsi_div',
                            'sig': 'buy',
                            'price': float(candles['c'][i]),
                            'time': int(candles['t'][i]),
                            'tf': timeframe,
                            'str': round(Decimal((100 - current_rsi - 10) / 100), 10)
                        })

            elif (current_rsi > params['sell']):
                if last_signal != 'sell':
                    last_signal = 'sell'
                    signals.append({
                        'indicator': 'rsi',
                        'sig': 'sell',
                        'price': float(candles['c'][i]),
                        'time': int(candles['t'][i]),
                        'tf': timeframe,
                        'str': round(Decimal((current_rsi - 10) / 100), 10)
                    })
                elif last_signal == 'sell':
                    # if our current price is higher than the current top,
                    # but we have a lower rsi (rsi double bottom signal)
                    if curr_price > top and current_rsi < rsi_total.iloc[top_index]:
                        last_signal = 'sell'
                        signals.append({
                            'indicator': 'rsi_div',
                            'sig': 'buy',
                            'price': float(candles['c'][i]),
                            'time': int(candles['t'][i]),
                            'tf': timeframe,
                            'str': round(Decimal((100 - current_rsi - 10) / 100), 10)
                        })

    print("printing rsi signals")
    for i in range(len(signals)):
        print(signals[i])

    return signals
