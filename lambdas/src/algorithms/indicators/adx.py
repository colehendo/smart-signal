import ta

# Average Directional Movement Index
# a little off, general trend is right tho
def run(params, candles, timeframe):
    all_adx = ta.trend.ADXIndicator(high = candles["h"], low = candles["l"], close = candles["c"], n = 14, fillna = False)
    print('Average Directional Movement Index')
    adx = all_adx.adx()
    print('adx: ', adx)
    neg = all_adx.adx_neg()
    print('neg adx: ', neg)
    pos = all_adx.adx_pos()
    print('pos adx: ', pos)