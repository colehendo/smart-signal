import ta

# Rate of Change
#gucci
def run(params, candles, timeframe):
    roc = ta.momentum.roc(close = candles["c"], n = 12, fillna = False)
    # print(' Rate of Change: ', roc)