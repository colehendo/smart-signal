import ta

# Vortex Indicator
def run(params, candles, timeframe):
    vi = ta.trend.VortexIndicator(high = candles["h"], low = candles["l"], close = candles["c"], n = 14, fillna = False)
    print('Vortex Indicator')
    vi_diff = vi.vortex_indicator_diff()
    print('vi_diff: ', vi_diff)
    vi_pos = vi.vortex_indicator_pos()
    print('vi_pos: ', vi_pos)
    vi_neg = vi.vortex_indicator_neg()
    print('vi_neg: ', vi_neg)