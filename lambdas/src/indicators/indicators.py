import time
from decimal import Decimal
import simplejson as json
from itertools import combinations
from multiprocessing import Process, Pipe

import pandas as pd
import ta

import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
dynamodb = boto3.resource('dynamodb')

#### SECTION FOR TESTING ALL COMBINATIONS ####

all_indicators = []
combo_results = []

month_candles = []
week_candles = []
day_candles = []
four_hour_candles = []
hour_candles = []
fifteen_minute_candles = []
minute_candles = []

month_ttl = 0
week_ttl = 0
day_ttl = 157680000
four_hour_ttl = 15768000
hour_ttl = 2628000
fifteen_minute_ttl = 604800
minute_ttl = 86400

def calculate(event, context):
    if (event['queryStringParameters'] == None):
        return {
            "statusCode": 502,
            "body": json.dumps("No parameters given"),
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }

    # Load the payload into a usable format
    data = json.loads(event['queryStringParameters']['vals'])

    if not data:
        return {
            "statusCode": 502,
            "body": json.dumps("No data given"),
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }

    # Remove the array of timeframes from the data
    timeframes = data[-1]
    del data[-1]

    if not data:
        return {
            "statusCode": 502,
            "body": "Data is in incorrect format",
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }

    timeframe_data = []
    all_signals = []
    final_signals = []

    global month_candles
    global week_candles
    global day_candles
    global four_hour_candles
    global hour_candles
    global fifteen_minute_candles
    global minute_candles

    # Condense all signals of all indicators for each timeframe given
    # into a single array, and append that array to the main array
    if ('month' in timeframes): month_candles = get_data('BTC_month', month_ttl)
    if ('week' in timeframes): week_candles = get_data('BTC_week', week_ttl)
    if ('day' in timeframes): day_candles = get_data('BTC_day', day_ttl)
    if ('four_hour' in timeframes): four_hour_candles = get_data('BTC_four_hour', four_hour_ttl)
    if ('hour' in timeframes): hour_candles = get_data('BTC_hour', hour_ttl)
    if ('fifteen_minute' in timeframes): fifteen_minute_candles = get_data('BTC_fifteen_minute', fifteen_minute_ttl)
    if ('minute' in timeframes): minute_candles = get_data('BTC_minute', minute_ttl)

    for indicator in data:
        result = run_indicator(indicator)
        if result:
            timeframe_data.append(result[0])
            for data in result[1]:
                all_signals.append(data)


    if not all_signals:
        return {
            "statusCode": 200,
            "body": json.dumps("No signals"),
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }

    else:
        return {
            "statusCode": 200,
            "body": json.dumps(reduce_tf(all_signals, timeframe_data)),
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }

def get_data(table, ttl):
    dynamo_table = dynamodb.Table(table)
    try:
        # Scan the table for all datapoints
        results = dynamo_table.scan()
    except ClientError as e:
        print(e.response['Error']['Code'])
        print(e.response['ResponseMetadata']['HTTPStatusCode'])
        print(e.response['Error']['Message'])
    else:
        if 'Items' in results:
            # Turn the returned object into a JSON string,
            # and pass it to pandas to make it readable for TA
            for i in range(len(results['Items'])):
                results['Items'][i]['t'] = results['Items'][i]['t'] - ttl
            return json.dumps(results['Items'])
        else:
            return []

def run_indicator(indicator):
    timeframe = indicator['timeframe']
    if indicator['timeframe'] == 'month': candles = month_candles
    elif indicator['timeframe'] == 'week': candles = week_candles
    elif indicator['timeframe'] == 'day': candles = day_candles
    elif indicator['timeframe'] == 'four_hour': candles = four_hour_candles
    elif indicator['timeframe'] == 'hour': candles = hour_candles
    elif indicator['timeframe'] == 'fifteen_minute': candles = fifteen_minute_candles
    elif indicator['timeframe'] == 'minute': candles = minute_candles

    if not candles:
        return []
    else:
        candles = pd.read_json(candles)

    indicator_data = match_indicator(indicator['indicator'], indicator['params'], candles, timeframe)

    if indicator_data:
        return ([{
            'indicator': indicator['indicator'],
            'tf': timeframe,
            'sig': 'hold',
            'str': 0,
            'start': candles['t'][0]
        },
        indicator_data])


def reduce_tf(all_signals, tf_signals):
    final_signals = []
    tf_sig_len = len(tf_signals)

    balance = 100000
    prev_buy = 0
    roi = 0
    total_roi = 0
    roi_count = 0

    overall_sig = "hold"

    for signal in all_signals:
        current_sig = signal['sig']
        current_tf = signal['tf']
        if current_sig != overall_sig:
            str_count = 0
            str_total = 0
            for i in range(tf_sig_len):
                if current_tf == tf_signals[i]['tf'] and signal['indicator'] == tf_signals[i]['indicator']:
                    if current_sig != tf_signals[i]['sig']:
                        tf_signals[i]['sig'] = current_sig
                        tf_signals[i]['str'] = signal['str']
                        str_total += signal['str']
                        str_count += 1
                else:
                    if current_sig != tf_signals[i]['sig'] and signal['time'] >= tf_signals[i]['start']:
                        break
                    elif tf_signals[i]['str'] != 0:
                        str_total += tf_signals[i]['str']
                        str_count += 1

                if i == (tf_sig_len - 1):
                    overall_sig = current_sig
                    transaction = (round(((str_total / str_count) * Decimal(signal['price'])), 10))
                    if (current_sig == 'buy'):
                        balance = round((balance - transaction), 2)
                        prev_buy = transaction
                        final_signals.append({
                            'sig': 'buy',
                            'time': signal['time'],
                            'amt': transaction
                        })

                    else:
                        balance = round((balance + transaction), 2)
                        if (prev_buy != 0):
                            roi = round((((transaction - prev_buy) / prev_buy) * 100), 6)
                            total_roi += roi
                            roi_count += 1

                        final_signals.append({
                            'sig': 'sell',
                            'time': signal['time'],
                            'amt': transaction,
                            'roi': roi
                        })

    if (roi_count == 0):
        final_signals.append({
            'bal': balance,
            'avg_roi': 0
        })
    else:
        final_signals.append({
            'bal': balance,
            'avg_roi': round(total_roi / roi_count, 6)
        })

    return final_signals
# A simple function to call the indicators.
# This may be better done with a struct
def match_indicator(indicator, params, candles, timeframe):
    if indicator in all_indicators:
        print(indicator)
        return all_indicators[indicator](params, candles)
    else:
        return []

    # ichimoku(params, candles)
    # sma(params, candles)



# THE END OF THE ARRAY CONTAINS THE LATEST VALUES


#
# # VOLUME
#
# # Accumulation/Distribution Index
# # Works best in a ranging period(so maybe after huge moves up or down),
# # does not work well when market is trending hard, good for locating trend reversals through top/bottom divergences
# # The AD line compares the strength of the open to the strength of the close divided by the range
# # drop this hoe
def adi(params, candles):
    adi = ta.volume.acc_dist_index(high = candles["h"], low = candles["l"], close = candles["c"], volume = candles["v"], fillna = False)
    print("Accumulation/Distribution Index")
    for i in range(0, len(adi)):
        if (i > (len(adi) - 10)):
            print('btc close: ', candles["c"][i], ' adi ', i, ': ', round(adi[i], 2))

# Chaikin Money Flow
# similar to MACD exccept also uses volume.
# uhh its kinda close but definitely a good bit off..leave it for now
def cmf(params, candles):
    cmf = ta.volume.chaikin_money_flow(high = candles["h"], low = candles["l"], close = candles["c"], volume = candles["v"], n = 20, fillna = False)
    print('Chaikin Money Flow')
    for i in range(0, len(cmf)):
        if (i > (len(cmf) - 10)):
            print('btc close: ', candles["c"][i], ' cmf ', i, ': ', round(cmf[i], 2))

# Ease of Movement
# drop this hoe
def eom(params, candles):
    eom = ta.volume.ease_of_movement(high = candles["h"], low = candles["l"], volume = candles["v"], n = 14, fillna = False)
    print('Ease of Movement')
    for i in range(0, len(eom)):
        if (i > (len(eom) - 10)):
            print('eom ', i, ': ', round(eom[i], 2))

# Force Index
# Multiplies the change in volume * price for each day
# probably drop this hoe bc too inconsistent
def fi(params, candles):
    fi = ta.volume.force_index(close = candles["c"], volume = candles["v"], n = 13, fillna = False)
    print('Force Index')
    for i in range(0, len(fi)):
        if (i > (len(fi) - 10)):
            print('fi ', i, ': ', round(fi[i], 2))

# Negative Volume Index
def nvi(params, candles):
    nvi = ta.volume.negative_volume_index(close = candles["c"], volume = candles["v"], fillna = False)
    print('Negative Volume Index')
    print(nvi)
    # for i in range(0, len(nvi)):
    #     if (i < 10) or (i > (len(nvi) - 10)):
    #         print('nvi ', i, ': ', nvi[i])

# On-Balance Volume
#Pretty pooop
def obv(params, candles):
    obv = ta.volume.on_balance_volume(close = candles["c"], volume = candles["v"], fillna = False)
    print('On-Balance Volume')
    for i in range(0, len(obv)):
        if (i > (len(obv) - 10)):
            print('btc close: ', candles["c"][i], ' obv ', i, ': ', round(obv[i], 2))

# Signal Ease of Movement
def seom(params, candles):
    seom = ta.volume.sma_ease_of_movement(high = candles["h"], low = candles["l"], volume = candles["v"], n = 14, fillna = False)
    print('Signal Ease of Movement')
    print(seom)
    for i in range(0, len(seom)):
        if (i > (len(seom) - 10)):
            print('seom ', i, ': ', round(seom[i], 2))

# Volume-price Trend
def vpt(params, candles):
    obv = ta.volume.on_balance_volume(close = candles["c"], volume = candles["v"], fillna = False)
    print('Volume-price Trend: ', vpt)
    # for i in range(0, len(vpt)):
    #     print(vpt[i])



# VOLATILITY

# Average True Range
# Pretty solid, maybe off like a few percent for each value
def atr(params, candles):
    atr = ta.volatility.average_true_range(high = candles["h"], low = candles["l"], close = candles["c"], n = 14, fillna = False)
    print('Average True Range: ', atr)

# Bollinger Bands
<<<<<<< HEAD
# Pretty accurate
def bb(params, candles):
    bb = ta.volatility.BollingerBands(close = candles["c"], n=20, ndev=2)
    mavg = bb.bollinger_mavg()
    print('Bollinger Bands')
    print('bb mavg: ', mavg)
    hband = bb.bollinger_hband()
    print('bb hband: ', hband)
    lband = bb.bollinger_lband()
    print('bb lband: ', lband)
    hband_i = bb.bollinger_hband_indicator() # idk what this is, get rid of these
    print('bb hband_i: ', hband_i)
    lband_i = bb.bollinger_lband_indicator() # idk what this is, get rid of these
    print('bb lband_i: ', lband_i)
    wband = bb.bollinger_wband() # idk what this is, get rid of these
    print('bb wband: ', wband)
    # pband = bb.bollinger_pband()
    # print('bb pband: ', pband)


#
#
#
=======
def bb(data):
    signals = []

    for i in range(len(data)):
        if (data['c'][i] < 7000):
            signals.append({'sig': 'buy', 'str': Decimal(.5)})
        elif (data['c'][i] > 8500):
            signals.append({'sig': 'sell', 'str': Decimal(.5)})
        else:
            signals.append({'sig': 'hold', 'str': 0})

    return signals

# Donchian Channel
def dc():
    print('dc')

# Keltner Channel
def kc():
    print('kc')



>>>>>>> 7158c62c1893642d6548ffd63cadd4a6b757c877
# TREND
#
# Average Directional Movement Index
# a little off, general trend is right tho
def adx(params, candles):
    all_adx = ta.trend.ADXIndicator(high = candles["h"], low = candles["l"], close = candles["c"], n = 14, fillna = False)
    print('Average Directional Movement Index')
    adx = all_adx.adx()
    print('adx: ', adx)
    neg = all_adx.adx_neg()
    print('neg adx: ', neg)
    pos = all_adx.adx_pos()
    print('pos adx: ', pos)


# Commodity Channel Index
def cci(params, candles):
    cci = ta.trend.cci(high = candles["h"], low = candles["l"], close = candles["c"], n = 20, c = 0.015, fillna = False)
    print('Commodity Channel Index: ', cci)




# Moving Average Convergence Divergence
# histogram and signal values match up, but the "macd signal one is not matching up well...this one represents the macd fast line on tradingview"
def macd(params, candles):
    all_macd = ta.trend.MACD(close = candles["c"], n_slow = 26, n_fast = 12, n_sign = 9, fillna = False)
    print('MACD')
    macd = all_macd.macd()
    print('macd: ', macd)
    macd_diff = all_macd.macd_diff()
    print('macd diff: ', macd_diff)
    macd_signal = all_macd.macd_signal()
    print('macd_signal: ', macd_signal)

# Mass Index
# good
def mi(params, candles):
    mi = ta.trend.mass_index(high = candles["h"], low = candles["l"], n = 10, n2 = 10, fillna = False)
    print('Mass Index: ', mi)

# Parabolic Stop And Reverse
# we'll trigger signals whenever we have a reversal so if
def psar(params, candles, timeframe):
    all_psar = ta.trend.PSARIndicator(high = candles["h"], low = candles["l"], close = candles["c"], step = 0.02, max_step = 0.2, fillna = False)
    print('Parabolic Stop And Reverse')
    psar = all_psar.psar()
    # print('psar: ', psar)
    psar_signals = []
    trend = "flat"
    last_signal = "hold"
    ##make sure to account for last signal
    for i in range(len(psar)):
        current_psar = psar.iloc[i]
        curr_price = candles["c"][i];
        if trend == "up" and current_psar > curr_price and last_signal != 'sell':
            last_signal = 'sell'
            psar_signals.append({
            'indicator': 'psar',
            'sig': 'sell',
            'price': float(candles['c'][i]),
            'time': int(candles['t'][i]),
            'tf': timeframe,
            'str': 100
            })
            trend = "down"
        elif trend == "down" and current_psar < curr_price and last_signal != 'buy':
            last_signal = 'buy'
            psar_signals.append({
            'indicator': 'psar',
            'sig': 'buy',
            'price': float(candles['c'][i]),
            'time': int(candles['t'][i]),
            'tf': timeframe,
            'str': 100
            })
            trend = "up"
        else:
            if current_psar > curr_price:
                trend = "down"
            elif current_psar < curr_price:
                trend = "up"
            else:
                trend = "flat"

    for i in range(0, len(psar_signals)):
        print(psar_signals[i][0])

    return psar_signals



# Simple Moving Average
#shit is broke
def sma(params, candles):
    sma = ta.trend.sma_indicator(close = candles["c"], n = 12, fillna = False)
    # print('sma: ', sma)


# Vortex Indicator
# solid
def vi(params, candles):
    vi = ta.trend.VortexIndicator(high = candles["h"], low = candles["l"], close = candles["c"], n = 14, fillna = False)
    # print('Vortex Indicator')
    # vi_diff = vi.vortex_indicator_diff() <-- probly useful when actually implementing
    # print('vi_diff: ', vi_diff)
    vi_pos = vi.vortex_indicator_pos()
    # print('vi_pos: ', vi_pos)
    vi_neg = vi.vortex_indicator_neg()
    # print('vi_neg: ', vi_neg)


# MOMENTUM

# Awesome Oscillator
# lil off but solid
def ao(params, candles):
    ao = ta.momentum.ao(high = candles["h"], low = candles["l"], s = 5, len = 34, fillna = False)
    # print('Awesome Oscillator: ', ao)

# Kaufman's Adaptive Moving Average
# good
def kama(params, candles):
    kama = ta.momentum.kama(close = candles["c"], n = 21, pow1 = 2, pow2 = 30, fillna = False)
    # print('Kaufmans Adaptive Moving Average: ', kama)

# Money Flow Index
# Basically an even better RSI indicator because it implements volume too.
# not good but fuk volume
def mfi(params, candles):
    mfi = ta.momentum.money_flow_index(high = candles["h"], low = candles["l"], close = candles["c"], volume = candles["v"], n = 14, fillna = False)
    # print('Money Flow Index')
    # print('mfi: ', mfi)
    # for i in range(0, len(mfi)):
    #     if (i < 10) or (i > (len(mfi) - 10)):
    #         print('mfi ', i, ': ', mfi[i])

# Rate of Change
#gucci
def roc(params, candles):
    roc = ta.momentum.roc(close = candles["c"], n = 12, fillna = False)
    # print(' Rate of Change: ', roc)

# Relative Strength Index
def rsi(params, candles, timeframe):
    # Get the past `timeframe` rsi values in a dataframe
    rsi_total = ta.momentum.rsi(close = candles["c"], n = 14, fillna = True)
    # print('params: ', params)

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

    return signals




# Stochastic Oscillator
#sr_sig correlates to the %K line on tradingview
def sr(params, candles):
    all_sr = ta.momentum.StochasticOscillator(high = candles["h"], low = candles["l"], close = candles["c"], n = 14, d_n = 3, fillna = False)
    print('HERE IS Stochastic Oscillator!!!!')
    sr_sig = all_sr.stoch_signal()
    print('sr_sig: ', sr_sig)

    signals = []
    for i in range(0, len(all_sr.stoch_signal())):
        curr_sr = all_sr.stoch_signal().iloc[i]
        if (curr_sr < 100) and (curr_sr > 0):
            if (curr_sr < params['buy']):
                # print('buy: ', i, ': ', curr_sr)
                signals.append({'sig': 'buy', 'str': round(Decimal((100 - curr_sr - 10) / 100), 10)})
            elif (curr_sr > params['sell']):
                # print('sell: ', i, ': ', curr_sr)
                signals.append({'sig': 'sell', 'str': round(Decimal((curr_sr - 10) / 100), 10)})
            else:
                signals.append({'sig': 'hold', 'str': 0})
        else:
            signals.append({'sig': 'hold', 'str': 0})

    return signals


#U ltimate Oscillator
# gucci
def uo(params, candles):
    uo = ta.momentum.uo(high = candles["h"], low = candles["l"], close = candles["c"], s = 7, m = 14, len = 28, ws = 4.0, wm = 2.0, wl = 1.0, fillna = False)
    # print('Ultimate Oscillator: ', uo)

# Williams %R
#gucci
def wr(params, candles):
    wr = ta.momentum.wr(high = candles["h"], low = candles["l"], close = candles["c"], lbp = 14, fillna = False)
    # print('Williams %R: ', wr)




all_indicators = {
    "adi": adi,
    "adx": adx,
    "ao": ao,
    "atr": atr,
    "bb": bb,
    "cci": cci,
    "cmf": cmf,
    "eom": eom,
    "fi": fi,
    "kama": kama,
    "macd": macd,
    "mfi": mfi,
    "mi": mi,
    "nvi": nvi,
    "obv": obv,
    "psar": psar,
    "roc": roc,
    "rsi": rsi,
    "seom": seom,
    "sr": sr,
    "uo": uo,
    "vi": vi,
    "vpt": vpt,
    "wr": wr
}
