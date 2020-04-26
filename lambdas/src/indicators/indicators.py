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

<<<<<<< HEAD
curr_time = int(time.time())
year_time = 31536000
month_time = 2628000
week_time = 604800
day_time = 86400

=======
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
>>>>>>> 7158c62c1893642d6548ffd63cadd4a6b757c877

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

    print('timeframes: ', timeframes)

    global month_candles
    global week_candles
    global day_candles
    global four_hour_candles
    global hour_candles
    global fifteen_minute_candles
    global minute_candles

    # Condense all signals of all indicators for each timeframe given
    # into a single array, and append that array to the main array
<<<<<<< HEAD
    if ('month' in timeframes):
        signals = condense_timeframe(data, get_data('BTC_month'), 'month', 0)
        if signals:
            all_signals.append(signals)
    if ('week' in timeframes):
        signals = condense_timeframe(data, get_data('BTC_week'), 'week', 0)
        if signals:
            all_signals.append(signals)
    if ('day' in timeframes):
        signals = condense_timeframe(data, get_data('BTC_day'), 'day', 157680000)
        if signals:
            all_signals.append(signals)
    if ('four_hour' in timeframes):
        signals = condense_timeframe(data, get_data('BTC_four_hour'), 'four_hour', 15768000)
        if signals:
            all_signals.append(signals)
    if ('hour' in timeframes):
        signals = condense_timeframe(data, get_data('BTC_hour'), 'hour', 2628000)
        if signals:
            all_signals.append(signals)
    if ('fifteen_minute' in timeframes):
        signals = condense_timeframe(data, get_data('BTC_fifteen_minute'), 'fifteen_minute', 604800)
        if signals:
            all_signals.append(signals)
    if ('minute' in timeframes):
        signals = condense_timeframe(data, get_data('BTC_minute'), 'minute', 86400)
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
=======
    if ('month' in timeframes): month_candles = get_data('BTC_month', month_ttl)
    if ('week' in timeframes): week_candles = get_data('BTC_week', week_ttl)
    if ('day' in timeframes): day_candles = get_data('BTC_day', day_ttl)
    if ('four_hour' in timeframes): four_hour_candles = get_data('BTC_four_hour', four_hour_ttl)
    if ('hour' in timeframes): hour_candles = get_data('BTC_hour', hour_ttl)
    if ('fifteen_minute' in timeframes): fifteen_minute_candles = get_data('BTC_fifteen_minute', fifteen_minute_ttl)
    if ('minute' in timeframes): minute_candles = get_data('BTC_minute', minute_ttl)

    for indicator in data:
        result = run_indicator(indicator)
        print('result: ', result)
        if result:
            timeframe_data.append(result[0])
            for data in result[1]:
                all_signals.append(data)
>>>>>>> 7158c62c1893642d6548ffd63cadd4a6b757c877


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
            print(json.dumps(results['Items']))
            return json.dumps(results['Items'])
        else:
            return []

<<<<<<< HEAD
def condense_timeframe(data, candles, timeframe, ttl):
    # Error catching for get_data
=======
def run_indicator(indicator):
    timeframe = indicator['timeframe']
    if indicator['timeframe'] == 'month': candles = month_candles
    elif indicator['timeframe'] == 'week': candles = week_candles
    elif indicator['timeframe'] == 'day': candles = day_candles
    elif indicator['timeframe'] == 'four_hour': candles = four_hour_candles
    elif indicator['timeframe'] == 'hour': candles = hour_candles
    elif indicator['timeframe'] == 'fifteen_minute': candles = fifteen_minute_candles
    elif indicator['timeframe'] == 'minute': candles = minute_candles

    print(candles)

>>>>>>> 7158c62c1893642d6548ffd63cadd4a6b757c877
    if not candles:
        print('not candle... :(')
        return []
    else:
        candles = pd.read_json(candles)
        # candles = ta.utils.dropna(candles)

<<<<<<< HEAD
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
                    'time': int(candles['t'][i]) - ttl,
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
                            'time': int(candles['t'][i]) - ttl,
                            'price': int(candles['c'][i])
                        })
=======
    print(candles)
>>>>>>> 7158c62c1893642d6548ffd63cadd4a6b757c877

    indicator_data = match_indicator(indicator['indicator'], indicator['params'], candles, timeframe)

    print(indicator_data)
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
    day_roi = 0
    day_roi_count = -1
    week_roi = 0
    week_roi_count = -1
    month_roi = 0
    month_roi_count = -1
    year_roi = 0
    year_roi_count = -1
    total_roi = 0
    total_roi_count = 0

<<<<<<< HEAD
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
                signal_time = all_signals[i]['time']
                # Calculate total roi, roi over past year, month, week, and day
                if (prev_buy != 0):
                    roi = (((transaction - prev_buy) / prev_buy) * 100)
                    total_roi += roi
                    total_roi_count += 1
                    if ((curr_time - signal_time) < year_time):
                        year_roi_count += 1
                        if (year_roi_count > 0):
                            year_roi += roi
                        if ((curr_time - signal_time) < month_time):
                            month_roi_count += 1
                            if (month_roi_count > 0):
                                month_roi += roi
                            if ((curr_time - signal_time) < week_time):
                                week_roi_count += 1
                                if (week_roi_count > 0):
                                    week_roi += roi
                                if ((curr_time - signal_time) < day_time):
                                    day_roi_count += 1
                                    if (day_roi_count > 0):
                                        day_roi += roi

                final_signals.append({
                    'sig': signal,
                    'time': signal_time,
                    'amt': transaction,
                    'roi': roi
                })

    final_signals.append({'bal': balance})
    if (day_roi_count > 0):
        final_signals.append({
            'day_roi': round(day_roi / day_roi_count, 6)
        })
    if (week_roi_count > 0):
        final_signals.append({
            'week_roi': round(week_roi / week_roi_count, 6)
        })
    if (month_roi_count > 0):
        final_signals.append({
            'month_roi': round(month_roi / month_roi_count, 6)
        })
    if (year_roi_count > 0):
        final_signals.append({
            'year_roi': round(year_roi / year_roi_count, 6)
        })
    if (total_roi_count > 0):
        final_signals.append({
            'avg_roi': round(total_roi / total_roi_count, 6)
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
    day_roi = 0
    day_roi_count = -1
    week_roi = 0
    week_roi_count = -1
    month_roi = 0
    month_roi_count = -1
    year_roi = 0
    year_roi_count = -1
    total_roi = 0
    total_roi_count = 0

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
=======
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
>>>>>>> 7158c62c1893642d6548ffd63cadd4a6b757c877
                        balance = round((balance - transaction), 2)
                        prev_buy = transaction
                        final_signals.append({
                            'sig': 'buy',
                            'time': signal['time'],
                            'amt': transaction
                        })

                    else:
                        balance = round((balance + transaction), 2)
                        # Calculate total roi, roi over past year, month, week, and day
                        if (prev_buy != 0):
                            roi = round((((transaction - prev_buy) / prev_buy) * 100), 6)
                            total_roi += roi
<<<<<<< HEAD
                            total_roi_count += 1
                            if ((curr_time - timestamp) < year_time):
                                year_roi_count += 1
                                if (year_roi_count > 0):
                                    year_roi += roi
                                if ((curr_time - timestamp) < month_time):
                                    month_roi_count += 1
                                    if (month_roi_count > 0):
                                        month_roi += roi
                                    if ((curr_time - timestamp) < week_time):
                                        week_roi_count += 1
                                        if (week_roi_count > 0):
                                            week_roi += roi
                                        if ((curr_time - timestamp) < day_time):
                                            day_roi_count += 1
                                            if (day_roi_count > 0):
                                                day_roi += roi
=======
                            roi_count += 1
>>>>>>> 7158c62c1893642d6548ffd63cadd4a6b757c877

                        final_signals.append({
                            'sig': 'sell',
                            'time': signal['time'],
                            'amt': transaction,
                            'roi': roi
                        })
<<<<<<< HEAD
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
                            # Calculate total roi, roi over past year, month, week, and day
                            if (prev_buy != 0):
                                roi = (((transaction - prev_buy) / prev_buy) * 100)
                                total_roi += roi
                                total_roi_count += 1
                                if ((curr_time - timestamp) < year_time):
                                    year_roi_count += 1
                                    if (year_roi_count > 0):
                                        year_roi += roi
                                    if ((curr_time - timestamp) < month_time):
                                        month_roi_count += 1
                                        if (month_roi_count > 0):
                                            month_roi += roi
                                        if ((curr_time - timestamp) < week_time):
                                            week_roi_count += 1
                                            if (week_roi_count > 0):
                                                week_roi += roi
                                            if ((curr_time - timestamp) < day_time):
                                                day_roi_count += 1
                                                if (day_roi_count > 0):
                                                    day_roi += roi

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


    final_signals.append({'bal': balance})
    if (day_roi_count > 0):
        final_signals.append({
            'day_roi': round(day_roi / day_roi_count, 6)
        })
    if (week_roi_count > 0):
        final_signals.append({
            'week_roi': round(week_roi / week_roi_count, 6)
        })
    if (month_roi_count > 0):
        final_signals.append({
            'month_roi': round(month_roi / month_roi_count, 6)
        })
    if (year_roi_count > 0):
        final_signals.append({
            'year_roi': round(year_roi / year_roi_count, 6)
        })
    if (total_roi_count > 0):
=======
    
    if (roi_count == 0):
        final_signals.append({
            'bal': balance,
            'avg_roi': 0
        })
    else:
>>>>>>> 7158c62c1893642d6548ffd63cadd4a6b757c877
        final_signals.append({
            'avg_roi': round(total_roi / total_roi_count, 6)
        })

    print('final signals: ', final_signals)

    return final_signals

# A simple function to call the indicators.
# This may be better done with a struct
<<<<<<< HEAD
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
    adx(params, candles)
    cci(params, candles)
    macd(params, candles)
    mi(params, candles)
    psar(params, candles)
    vi(params, candles)
    ao(params, candles)
    kama(params, candles)
    mfi(params, candles)
    roc(params, candles)
    sr(params, candles)
    uo(params, candles)
    wr(params, candles)

    if indicator in all_indicators:
        print(indicator)
        return all_indicators[indicator](params, candles)
=======
def match_indicator(indicator, params, candles, timeframe):
    if (indicator == 'rsi'):
        return rsi(params, candles, timeframe)
    elif (indicator == 'macd'):
        return macd(candles)
    elif (indicator == 'bb'):
        return bb(candles)
>>>>>>> 7158c62c1893642d6548ffd63cadd4a6b757c877
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

<<<<<<< HEAD
# Mass Index
# good
def mi(params, candles):
    mi = ta.trend.mass_index(high = candles["h"], low = candles["l"], n = 10, n2 = 10, fillna = False)
    print('Mass Index: ', mi)

# Parabolic Stop And Reverse
# we'll trigger signals whenever we have a reversal so if
def psar(params, candles):
    all_psar = ta.trend.PSARIndicator(high = candles["h"], low = candles["l"], close = candles["c"], step = 0.02, max_step = 0.2, fillna = False)
    print('Parabolic Stop And Reverse')
    psar = all_psar.psar()
    # print('psar: ', psar)
    psar_signals = []
    trend = "flat"
    for i in range(0, len(psar)):
        current_psar = psar.iloc[i]
        curr_price = candles["c"][i];
        if trend == "up" and current_psar > curr_price:
            psar_signals.append({'sig': 'sell', 'str': 100})
            trend = "down"
        elif trend == "down" and current_psar < curr_price:
            psar_signals.append({'sig': 'buy', 'str': 100})
            trend = "up"
=======
    for i in range(len(data)):
        if (data['c'][i] < 6500):
            signals.append({'sig': 'buy', 'str': Decimal(.5)})
        elif (data['c'][i] > 8000):
            signals.append({'sig': 'sell', 'str': Decimal(.5)})
>>>>>>> 7158c62c1893642d6548ffd63cadd4a6b757c877
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
<<<<<<< HEAD
def rsi(params, candles):
    print('rsi!!!!')
    # Get the past `timeframe` rsi values in a dataframe
    rsi_total = ta.momentum.rsi(close = candles["c"], n = 14, fillna = True)
    # print('params: ', params)
    # print(' rsi: ', rsi_total)
=======
def rsi(params, candles, timeframe):
    # Get the past `timeframe` rsi values in a dataframe
    rsi_total = ta.momentum.rsi(close = candles["c"], n = 14, fillna = True)
    # print('params: ', params)
>>>>>>> 7158c62c1893642d6548ffd63cadd4a6b757c877

    signals = []
    last_signal = 'hold'

    for i in range(len(rsi_total)):
        current_rsi = rsi_total.iloc[i]
        if (current_rsi < 100) and (current_rsi > 0):
<<<<<<< HEAD
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
=======
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


def rsi_test(params, candles, timeframe):
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
>>>>>>> 7158c62c1893642d6548ffd63cadd4a6b757c877

    print('rsi: ', signals)
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
