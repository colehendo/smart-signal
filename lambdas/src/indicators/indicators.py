import time
from decimal import Decimal
import simplejson as json
import pandas as pd
import ta

import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
dynamodb = boto3.resource('dynamodb')

def calculate(event, context):
    if (event['queryStringParameters'] == None):
        return {
            "statusCode": 502,
            "body": "No parameters given",
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }

    # Load the payload into a usable format
    data = json.loads(event['queryStringParameters']['vals'])

    if not data:
        return {
            "statusCode": 502,
            "body": "No data given",
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }

    # Remove the array of timeframes from the data
    timeframes = data[len(data) - 1]
    del data[-1]

    if not data:
        return {
            "statusCode": 502,
            "body": "Data is in incorrect format",
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }

    all_signals = []
    final_signals = []

    # Condense all signals of all indicators for each timeframe given
    # into a single array, and append that array to the main array
    if ('month' in timeframes):
        signals = condense_timeframe(data, get_data('BTC_month'), 'month')
        if signals:
            all_signals.append(signals)
    if ('week' in timeframes):
        signals = condense_timeframe(data, get_data('BTC_week'), 'week')
        if signals:
            all_signals.append(signals)
    if ('day' in timeframes):
        signals = condense_timeframe(data, get_data('BTC_day'), 'day')
        if signals:
            all_signals.append(signals)
    if ('four_hour' in timeframes):
        signals = condense_timeframe(data, get_data('BTC_four_hour'), 'four_hour')
        if signals:
            all_signals.append(signals)
    if ('hour' in timeframes):
        signals = condense_timeframe(data, get_data('BTC_hour'), 'hour')
        if signals:
            all_signals.append(signals)
    if ('fifteen_minute' in timeframes):
        signals = condense_timeframe(data, get_data('BTC_fifteen_minute'), 'fifteen_minute')
        if signals:
            all_signals.append(signals)
    if ('minute' in timeframes):
        signals = condense_timeframe(data, get_data('BTC_minute'), 'minute')
        if signals:
            all_signals.append(signals)

    if not all_signals:
        return {
            "statusCode": 200,
            "body": "No signals",
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }

    a_s_length = len(all_signals)

    if (a_s_length == 1):
        return {
            "statusCode": 200,
            "body": json.dumps(one_tf(all_signals[0])),
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }

    else:
        return {
            "statusCode": 200,
            "body": json.dumps(multi_tf(all_signals, a_s_length)),
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }

def get_data(table):
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
            return json.dumps(results['Items'])
        else:
            return []

def condense_timeframe(data, candles, timeframe):
    # Error catching for get_data
    if not candles:
        return []
    else:
        candles = pd.read_json(candles)
        # candles = ta.utils.dropna(candles)

    timeframe_data = []
    timeframe_signals = []

    # If an indicator is requested on this timeframe,
    # append that indicator's data to an array
    for i in range(0, len(data)):
        if (data[i]['timeframe'] == timeframe):
            indicator = match_indicator(data[i]['indicator'], data[i]['params'], candles)
            if indicator:
                timeframe_data.append(indicator)

    # Error catching for no signals returned
    if not timeframe_data:
        return []

    t_d_length = len(timeframe_data)

    # If only one indicator returned signals
    # make an array of signals different from the
    # one before and the one after it
    if (t_d_length == 1):
        for i in range(0, len(candles)):
            signal = timeframe_data[0][i]['sig']
            if ((not timeframe_signals) or (signal != timeframe_signals[len(timeframe_signals) - 1]['sig'])):
                timeframe_signals.append({
                    'sig': signal,
                    'str': timeframe_data[0][i]['str'],
                    'time': int(candles['t'][i]),
                    'price': int(candles['c'][i])
                })

    # Go through each indicator's signal at a given index.
    # If all signals match at one index, calculate the avg
    # strength of all those signals and append it to a final array
    else:
        strength = 0
        for i in range (0, len(candles)):
            signal = timeframe_data[0][i]['sig']
            if ((not timeframe_signals) or (signal != timeframe_signals[len(timeframe_signals) - 1]['sig'])):
                strength += timeframe_data[0][i]['str']
                for j in range (1, t_d_length):
                    if (timeframe_data[j][i]['sig'] != signal):
                        break

                    elif (j == (t_d_length - 1)):
                        final_strength = round((strength / t_d_length), 10)
                        timeframe_signals.append({
                            'sig': signal,
                            'str': final_strength,
                            'time': int(candles['t'][i]),
                            'price': int(candles['c'][i])
                        })

                        strength = 0
                        break

                    else:
                        strength += timeframe_data[j][i]['str']

    return timeframe_signals

# Function called if singal timeframe given
def one_tf(all_signals):
    final_signals = []

    balance = 100000
    prev_buy = 0
    roi = 0
    total_roi = 0
    roi_count = 0

    # Run a loop over the signals given.
    # Remove all hold signals.
    # Calculate ROI for any sell that comes after a buy.
    # Calculate transaction amounts based on strength of the signal.
    for i in range(0, len(all_signals)):
        signal = all_signals[i]['sig']
        if (signal != 'hold' and ((not final_signals) or (signal != final_signals[len(final_signals) - 1]['sig']))):
            transaction = (all_signals[i]['str'] * all_signals[i]['price'])
            if (signal == 'buy'):
                balance = round((balance - transaction), 2)
                prev_buy = transaction
                final_signals.append({
                    'sig': signal,
                    'time': all_signals[i]['time'],
                    'amt': transaction
                })

            else:
                balance = round((balance + transaction), 2)
                if (prev_buy != 0):
                    roi = (((transaction - prev_buy) / prev_buy) * 100)
                    total_roi += roi
                    roi_count += 1

                final_signals.append({
                    'sig': signal,
                    'time': all_signals[i]['time'],
                    'amt': transaction,
                    'roi': roi
                })

    if (roi_count == 0):
        final_signals.append({'bal': balance})
    else:
        final_signals.append({
            'bal': balance,
            'avg_roi': round(total_roi / roi_count, 6)
        })

    return final_signals

# Function called if singal timeframe given
def multi_tf(all_signals, a_s_length):
    final_signals = []
    a_s_record = []

    signal = all_signals[0][0]['sig']
    strength = all_signals[0][0]['str']
    str_count = 1
    timestamp = all_signals[0][0]['time']
    tf = 1
    balance = 100000
    prev_buy = 0
    roi = 0
    total_roi = 0
    roi_count = 0

    # This keeps track of the current signal being looked at
    # for each timeframe and the final signal for each timeframe.
    # This lets us not look through old data and error catches
    # going past the last index
    for i in range(0, a_s_length):
        a_s_record.append([0, len(all_signals[i])])

    # Loop through the largest timeframe's signals.
    # For each timeframe given, look at all the signals between
    # the next biggest (parent's) timeframe's current signal timestamp
    # and its next signal timestamp. Try to find a matching signal
    # for the current timeframe in that gap of its parent's.
    # If the smallest timeframe has been reached and all timeframes
    # have a signal matching within the scope of their parent,
    # calculate strength, ROI, transaction, and a new balance,
    # and append the signal to a final array
    while (a_s_record[0][0] < a_s_record[0][1]):
        if (signal != 'hold' and ((not final_signals) or (signal != final_signals[len(final_signals) - 1]['sig']))):
            if ((a_s_record[tf - 1][0] + 1) < a_s_record[tf - 1][1]):
                # If current timeframe's first signal is past its parent's next signal, send signal
                prev_too_early = all_signals[tf][0]['time'] >= all_signals[tf - 1][a_s_record[tf - 1][0] + 1]['time']
                # If current signal is past its parent's next signal
                current_too_late = all_signals[tf][a_s_record[tf][0]]['time'] >= all_signals[tf - 1][a_s_record[tf - 1][0] + 1]['time']

                if (prev_too_early):
                    final_strength = round(Decimal(strength / str_count), 10)
                    transaction = round((final_strength * round(Decimal(all_signals[tf][a_s_record[tf][0]]['price']), 6)), 2)
                    # print('strength: ', strength, ' str count: ', str_count, ' final str: ', final_strength)
                    # print('price: ', all_signals[tf][a_s_record[tf][0]]['price'], ' transaction: ', transaction)
                    # print(all_signals[tf][a_s_record[tf][0]])
                    if (signal == 'buy'):
                        balance = round((balance - transaction), 2)
                        prev_buy = transaction
                        final_signals.append({
                            'sig': signal,
                            'time': timestamp,
                            'amt': transaction
                        })

                    else:
                        balance = round((balance + transaction), 2)
                        if (prev_buy != 0):
                            roi = (((transaction - prev_buy) / prev_buy) * 100)
                            total_roi += roi
                            roi_count += 1

                        final_signals.append({
                            'sig': signal,
                            'time': timestamp,
                            'amt': transaction,
                            'roi': roi
                        })
                    a_s_record[0][0] += 1
                    tf = 1
                    signal = all_signals[0][a_s_record[0][0]]['sig']
                    strength = all_signals[0][a_s_record[0][0]]['str']
                    str_count = 1
                    timestamp = all_signals[0][a_s_record[0][0]]['time']
                    continue

                elif (current_too_late):
                    tf -= 1
                    a_s_record[tf][0] += 1
                    if (tf == 0):
                        tf = 1
                        signal = all_signals[0][a_s_record[0][0]]['sig']
                        strength = all_signals[0][a_s_record[0][0]]['str']
                        str_count = 1
                        timestamp = all_signals[0][a_s_record[0][0]]['time']
                    continue

            # If its the right signal
            if (all_signals[tf][a_s_record[tf][0]]['sig'] == signal):
                # If the signal's timestamp is >= than that of its parent's current signal
                sig_past_parent = all_signals[tf][a_s_record[tf][0]]['time'] >= all_signals[tf - 1][a_s_record[tf - 1][0]]['time']

                if ((a_s_record[tf][0] + 1) == a_s_record[tf][1]):
                    next_sig_past_parent = False
                else:
                    # If the signal's next timestamp is > than that of its parent's current signal
                    next_sig_past_parent = all_signals[tf][a_s_record[tf][0] + 1]['time'] > all_signals[tf - 1][a_s_record[tf - 1][0]]['time']
                if (sig_past_parent or next_sig_past_parent):
                    # This is the new earliest time this signal can fire
                    if (sig_past_parent):
                        timestamp = all_signals[tf][a_s_record[tf][0]]['time']
                    # If the smallest timeframe has been reached, send the signal
                    if (tf == (a_s_length - 1)):
                        final_strength = round(Decimal(strength / str_count), 10)
                        transaction = round((final_strength * round(Decimal(all_signals[tf][a_s_record[tf][0]]['price']), 6)), 2)
                        # print('strength: ', strength, ' str count: ', str_count, ' final str: ', final_strength)
                        # print('price: ', all_signals[tf][a_s_record[tf][0]]['price'], ' transaction: ', transaction)
                        if (signal == 'buy'):
                            balance = round((balance - transaction), 2)
                            prev_buy = transaction
                            final_signals.append({
                                'sig': signal,
                                'time': timestamp,
                                'amt': transaction
                            })

                        else:
                            balance = round((balance + transaction), 2)
                            if (prev_buy != 0):
                                roi = (((transaction - prev_buy) / prev_buy) * 100)
                                total_roi += roi
                                roi_count += 1

                            final_signals.append({
                                'sig': signal,
                                'time': timestamp,
                                'amt': transaction,
                                'roi': roi
                            })
                        tf = 1
                        a_s_record[0][0] += 1
                        signal = all_signals[0][a_s_record[0][0]]['sig']
                        strength = all_signals[0][a_s_record[0][0]]['str']
                        str_count = 1
                        timestamp = all_signals[0][a_s_record[0][0]]['time']
                        continue

                    else:
                        strength += all_signals[tf][a_s_record[tf][0]]['str']
                        str_count += 1
                        tf += 1

                else:
                    a_s_record[tf][0] += 1
                    if (a_s_record[tf][0] == a_s_record[tf][1]):
                        break

            else:
                a_s_record[tf][0] += 1
                if (a_s_record[tf][0] == a_s_record[tf][1]):
                    break

        else:
            tf = 1
            a_s_record[0][0] += 1
            if (a_s_record[0][0] == a_s_record[0][1]):
                break

            signal = all_signals[0][a_s_record[0][0]]['sig']
            strength = all_signals[0][a_s_record[0][0]]['str']
            str_count = 1
            timestamp = all_signals[0][a_s_record[0][0]]['time']
            continue


    if (roi_count == 0):
        final_signals.append({'bal': balance})
    else:
        final_signals.append({
            'bal': balance,
            'avg_roi': round(total_roi / roi_count, 6)
        })

    return final_signals

# A simple function to call the indicators.
# This may be better done with a struct
def match_indicator(indicator, params, candles):
    adi(params, candles)
    cmf(params, candles)
    eom(params, candles)
    fi(params, candles)
    nvi(params, candles)
    obv(params, candles)
    seom(params, candles)
    vpt(params, candles)
    atr(params, candles)
    bb(params, candles)
    dc(params, candles)
    kc(params, candles)
    adx(params, candles)
    aroon(params, candles)
    cci(params, candles)
    dpo(params, candles)
    kst(params, candles)
    macd(params, candles)
    mi(params, candles)
    psar(params, candles)
    trix(params, candles)
    vi(params, candles)
    ao(params, candles)
    kama(params, candles)
    mfi(params, candles)
    roc(params, candles)
    sr(params, candles)
    tsi(params, candles)
    uo(params, candles)
    wr(params, candles)
    cr(params, candles)
    dlr(params, candles)
    dr(params, candles)

    # ichimoku(params, candles)
    # sma(params, candles)

    if (indicator == 'rsi'):
        return rsi(params, candles)
    elif (indicator == 'macd'):
        return macd(candles)
    elif (indicator == 'bb'):
        return bb(candles)
    else:
        return []



# THE END OF THE ARRAY CONTAINS THE LATEST VALUES



# VOLUME

# Accumulation/Distribution Index
# Works best in a ranging period(so maybe after huge moves up or down),
# does not work well when market is trending hard, good for locating trend reversals through top/bottom divergences
# The AD line compares the strength of the open to the strength of the close divided by the range
# drop this hoe
def adi(params, candles):
    adi = ta.volume.acc_dist_index(high = candles["h"], low = candles["l"], close = candles["c"], volume = candles["v"], fillna = False)
    print("Accumulation/Distribution Index")
    for i in range(0, len(adi)):
        if (i > (len(adi) - 10)):
            print('adi ', i, ': ', round(adi[i], 2))

# Chaikin Money Flow
# similar to MACD exccept also uses volume.
# uhh its kinda close but definitely a good bit off..leave it for now
def cmf(params, candles):
    cmf = ta.volume.chaikin_money_flow(high = candles["h"], low = candles["l"], close = candles["c"], volume = candles["v"], n = 20, fillna = False)
    print('Chaikin Money Flow')
    for i in range(0, len(cmf)):
        if (i > (len(cmf) - 10)):
            print('cmf ', i, ': ', round(cmf[i], 2))

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
            print('obv ', i, ': ', round(obv[i], 2))

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

# Donchian Channel
# drop this hoe
def dc(params, candles):
    dc = ta.volatility.DonchianChannel(close = candles["c"], n=20, fillna = False)
    print('Donchian Channel')
    hband = dc.donchian_channel_hband()
    print('dc hband: ', hband)
    hband_i = dc.donchian_channel_hband_indicator()
    print('dc hband_i: ', hband_i)
    lband = dc.donchian_channel_lband()
    print('dc lband: ', lband)
    lband_i = dc.donchian_channel_lband_indicator()
    print('dc lband_i: ', lband_i)

# Keltner Channel
# drop this hoe
def kc(params, candles):
    kc = ta.volatility.KeltnerChannel(high = candles["h"], low = candles["l"], close = candles["c"], n = 14, fillna = False)
    print('Keltner Channel')
    # mband = kc.keltner_channel_mband()
    # print('kc mband: ', mband)
    hband = kc.keltner_channel_hband()
    print('kc hband: ', hband)
    lband = kc.keltner_channel_lband()
    print('kc lband: ', lband)
    hband_i = kc.keltner_channel_hband_indicator() ##remove this idk what they do
    print('kc hband_i: ', hband_i)
    lband_i = kc.keltner_channel_lband_indicator() ##remove this idk what they do
    print('kc lband_i: ', lband_i)
    # wband = kc.keltner_channel_wband()
    # print('kc wband: ', wband)
    # pband = kc.keltner_channel_pband()
    # print('kc pband: ', pband)



# TREND

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

# Aroon Indicator
# i hate this name drop this hoe
def aroon(params, candles):
    aroon = ta.trend.AroonIndicator(close = candles["c"], n = 25, fillna = False)
    print('Aroon Indicator')
    down = aroon.aroon_down()
    print('aroon down: ', down)
    up = aroon.aroon_up()
    print('aroon up: ', up)
    indicator = aroon.aroon_indicator()
    print('aroon indicator: ', indicator)

# Commodity Channel Index
def cci(params, candles):
    cci = ta.trend.cci(high = candles["h"], low = candles["l"], close = candles["c"], n = 20, c = 0.015, fillna = False)
    print('Commodity Channel Index: ', cci)

# Detrended Price Oscillator
# drop this hoe hella inaccurate
def dpo(params, candles):
    dpo = ta.trend.dpo(close = candles["c"], n = 20, fillna = False)
    print('Detrended Price Oscillator: ', dpo)

# Ichimoku Kinkō Hyō
def ichimoku(params, candles):
    ichimoku = ta.trend.IchimokuIndicato(high = candles["h"], low = candles["l"], n1 = 9, n2 = 26, n3 = 52, visual = False, fillna = False)
    print('ichi: ', ichimoku)
    ichimoku_a = ichimoku.ichimoku_a()
    print('ichi a: ', ichimoku_a)
    ichimoku_b = ichimoku.ichimoku_b()
    print('ichi b: ', ichimoku_b)

# KST Oscillator
# delete the kst diff it doesnt relate to tradingview shit
def kst(params, candles):
    all_kst = ta.trend.KSTIndicator(close = candles["c"], r1 = 10, r2 = 15, r3 = 20, r4 = 30, n1 = 10, n2 = 10, n3 = 10, n4 = 15, nsig = 9, fillna = False)
    print('KST Oscillator')
    kst = all_kst.kst()
    print('kst: ', kst)
    kst_diff = all_kst.kst_diff()
    print('kst diff: ', kst_diff)
    kst_sig = all_kst.kst_sig()
    print('kst_sig: ', kst_sig)

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
def mi(params, candles):
    mi = ta.trend.mass_index(high = candles["h"], low = candles["l"], n = 9, n2 = 25, fillna = False)
    print('Mass Index: ', mi)

# Parabolic Stop And Reverse
def psar(params, candles):
    all_psar = ta.trend.PSARIndicator(high = candles["h"], low = candles["l"], close = candles["c"], step = 0.02, max_step = 0.2, fillna = False)
    print('Parabolic Stop And Reverse')
    psar = all_psar.psar()
    print('psar: ', psar)
    psar_down = all_psar.psar_down()
    print('psar_down: ', psar_down)
    psar_down_i = all_psar.psar_down_indicator()
    print('psar_down_i: ', psar_down_i)
    psar_up = all_psar.psar_up()
    print('psar_up: ', psar_up)
    psar_up_i = all_psar.psar_up_indicator()
    print('psar_up_i: ', psar_up_i)

# Simple Moving Average
def sma(params, candles):
    sma = ta.trend.sma_indicator(close = candles["c"], n = 12, fillna = False)
    print('sma: ', sma)

# Trix
def trix(params, candles):
    trix = ta.trend.trix(close = candles["c"], n = 15, fillna = False)
    print('trix: ', trix)

# Vortex Indicator
def vi(params, candles):
    vi = ta.trend.VortexIndicator(high = candles["h"], low = candles["l"], close = candles["c"], n = 14, fillna = False)
    print('Vortex Indicator')
    vi_diff = vi.vortex_indicator_diff()
    print('vi_diff: ', vi_diff)
    vi_pos = vi.vortex_indicator_pos()
    print('vi_pos: ', vi_pos)
    vi_neg = vi.vortex_indicator_neg()
    print('vi_neg: ', vi_neg)


# MOMENTUM

# Awesome Oscillator
def ao(params, candles):
    ao = ta.momentum.ao(high = candles["h"], low = candles["l"], s = 5, len = 34, fillna = False)
    print('Awesome Oscillator: ', ao)

# Kaufman's Adaptive Moving Average
def kama(params, candles):
    kama = ta.momentum.kama(close = candles["c"], n = 10, pow1 = 2, pow2 = 30, fillna = False)
    print('Kaufmans Adaptive Moving Average: ', kama)

# Money Flow Index
# Basically an even better RSI indicator because it implements volume too.
def mfi(params, candles):
    mfi = ta.momentum.money_flow_index(high = candles["h"], low = candles["l"], close = candles["c"], volume = candles["v"], n = 14, fillna = False)
    print('Money Flow Index')
    print(mfi)
    # for i in range(0, len(mfi)):
    #     if (i < 10) or (i > (len(mfi) - 10)):
    #         print('mfi ', i, ': ', mfi[i])

# Rate of Change
def roc(params, candles):
    roc = ta.momentum.roc(close = candles["c"], n = 12, fillna = False)
    print('Rate of Change: ', roc)

# Relative Strength Index
def rsi(params, candles):
    # Get the past `timeframe` rsi values in a dataframe
    rsi_total = ta.momentum.rsi(close = candles["c"], n = 14, fillna = True)
    # print('params: ', params)
    # print('rsi: ', rsi)

    signals = []

    for i in range(0, len(rsi_total)):
        current_rsi = rsi_total.iloc[i]
        if (current_rsi < 100) and (current_rsi > 0):
            if (current_rsi < params['buy']):
                # print('buy: ', i, ': ', current_rsi)
                signals.append({'sig': 'buy', 'str': round(Decimal((100 - current_rsi - 10) / 100), 10)})
            elif (current_rsi > params['sell']):
                # print('sell: ', i, ': ', current_rsi)
                signals.append({'sig': 'sell', 'str': round(Decimal((current_rsi - 10) / 100), 10)})
            else:
                signals.append({'sig': 'hold', 'str': 0})
        else:
            signals.append({'sig': 'hold', 'str': 0})

    return signals

# Stochastic Oscillator
def sr(params, candles):
    all_sr = ta.momentum.StochasticOscillator(high = candles["h"], low = candles["l"], close = candles["c"], n = 14, d_n = 3, fillna = False)
    print('Stochastic Oscillator')
    sr = all_sr.stoch()
    print('sr: ', sr)
    sr_sig = all_sr.stoch_signal()
    print('sr_sig: ', sr_sig)

# True strength index
def tsi(params, candles):
    tsi = ta.momentum.tsi(close = candles["c"], r = 25, s = 13, fillna = False)
    print('True strength index: ', tsi)

# Ultimate Oscillator
def uo(params, candles):
    uo = ta.momentum.uo(high = candles["h"], low = candles["l"], close = candles["c"], s = 7, m = 14, len = 28, ws = 4.0, wm = 2.0, wl = 1.0, fillna = False)
    print('Ultimate Oscillator: ', uo)

# Williams %R
def wr(params, candles):
    wr = ta.momentum.wr(high = candles["h"], low = candles["l"], close = candles["c"], lbp = 14, fillna = False)
    print('Williams %R: ', wr)



# OTHERS

# Cumulative Return
def cr(params, candles):
    ta.others.cumulative_return(close = candles["c"], fillna = False)
    print('Cumulative Return: ', cr)

# Daily Log Return
def dlr(params, candles):
    dlr = ta.others.daily_log_return(close = candles["c"], fillna = False)
    print('Daily Log Return: ', dlr)

# Daily Return
def dr(params, candles):
    dr = ta.others.daily_return(close = candles["c"], fillna = False)
    print('Daily Return: ', dr)
