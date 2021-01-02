import ta

# Moving Average Convergence Divergence
# histogram and signal values match up, but the "macd signal one is not matching up well...
# this one represents the macd fast line on tradingview"
def run(params, candles, timeframe):
    macd = ta.trend.macd_diff(close = candles["c"], n_slow = 26, n_fast = 12, n_sign = 9, fillna = False)
    print('MACD')
    signals = []
    last_signal = "hold"
    for i in range(1, len(macd)):
        curr_macd = macd.iloc[i]
        next_macd = macd.iloc[i+1]
        # to avoid out of bounds
        if i+1 == len(macd) - 1:
            break
        #if we go from negative to positive indicates bullish trend so buy
        elif curr_macd <= 0 and next_macd > 0 and last_signal != "buy":
            last_signal = "buy"
            signals.append({
            'indicator': 'macd',
            'sig': 'buy',
            'price': float(candles['c'][i]),
            'time': int(candles['t'][i]),
            'tf': timeframe,
            'str': 100
            })
        #if we our macd is positive and goes to negative then indicates bearish trend so sell
        elif curr_macd <= 0 and next_macd > 0 and last_signal != "sell":
            last_signal = "sell"
            signals.append({
            'indicator': 'macd',
            'sig': 'sell',
            'price': float(candles['c'][i]),
            'time': int(candles['t'][i]),
            'tf': timeframe,
            'str': 100
            })

    print("printing MACD signals")
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
    # macd = macd.macd()
    # print('macd: ', macd)
    # macd_diff = macd.macd_diff()
    # print('macd diff: ', macd_diff)
    # macd_signal = macd.macd_signal()
    # print('macd_signal: ', macd_signal)
