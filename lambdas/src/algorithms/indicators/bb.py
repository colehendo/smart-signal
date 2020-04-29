import ta

# Bollinger Bands
# Pretty accurate
def run(params, candles, timeframe):
    bb = ta.volatility.BollingerBands(close = candles["c"], n=20, ndev=2)
    all_adx = ta.trend.ADXIndicator(high = candles["h"], low = candles["l"], close = candles["c"], n = 14, fillna = False)
    adx = all_adx.adx()
    mavg = bb.bollinger_mavg()
    neg = all_adx.adx_neg()
    pos = all_adx.adx_pos()
    print('Bollinger Bands')
    print('bb mavg: ', mavg)
    hband = bb.bollinger_hband()
    print('bb hband: ', hband)
    lband = bb.bollinger_lband()
    print('bb lband: ', lband)

    signals = []
    last_signal = "hold"
    for i in range(len(hband)):
        curr_adx = adx.iloc[i]
        curr_price = candles["c"][i]
        curr_lband = lband.iloc[i]
        curr_hband = hband.iloc[i]
        curr_neg = neg.iloc[i]
        curr_pos = pos.iloc[i]
        #   this is important because if adx is below 27 we are not trending
        #   this indicator works well in ranging markets
        if curr_adx < 27:
            if curr_pos < curr_neg:
                if closeEnough(curr_price, curr_lband) == True and last_signal != "buy":
                    last_signal = "buy"
                    signals.append({
                    'indicator': 'bb',
                    'sig': 'buy',
                    'price': float(candles['c'][i]),
                    'time': int(candles['t'][i]),
                    'tf': timeframe,
                    'str': 100
                    })
            elif curr_pos > curr_neg:
                if (closeEnough(curr_price, curr_hband)) == True and last_signal != "sell":
                    last_signal = "sell"
                    signals.append({
                    'indicator': 'bb',
                    'sig': 'sell',
                    'price': float(candles['c'][i]),
                    'time': int(candles['t'][i]),
                    'tf': timeframe,
                    'str': 100
                    })

    print("printing BB signals")
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

def closeEnough(curr_price, band_price):
    num = 0.02*band_price
    diff = abs(band_price - curr_price)
    if num - diff > 0:
        return True
    else:
        return False
