import ta

# Money Flow Index
# Basically an even better RSI indicator because it implements volume too.
# not good but fuk volume
def run(params, candles, timeframe):
    mfi = ta.momentum.money_flow_index(high = candles["h"], low = candles["l"], close = candles["c"], volume = candles["v"], n = 14, fillna = False)
    # print('Money Flow Index')
    # print('mfi: ', mfi)
    # for i in range(0, len(mfi)):
    #     if (i < 10) or (i > (len(mfi) - 10)):
    #         print('mfi ', i, ': ', mfi[i])