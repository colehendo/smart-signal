import time
from decimal import Decimal
import simplejson as json
from itertools import combinations

import pandas as pd
import ta

import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
dynamodb = boto3.resource('dynamodb')

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
            "body": "No parameters given",
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }
    print(event['queryStringParameters'])

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
        signals = condense_timeframe(data, get_data('BTC_month', month_ttl), 'month')
        if signals:
            all_signals.append(signals)
    if ('week' in timeframes):
        signals = condense_timeframe(data, get_data('BTC_week', week_ttl), 'week')
        if signals:
            all_signals.append(signals)
    if ('day' in timeframes):
        signals = condense_timeframe(data, get_data('BTC_day', day_ttl), 'day')
        if signals:
            all_signals.append(signals)
    if ('four_hour' in timeframes):
        signals = condense_timeframe(data, get_data('BTC_four_hour', four_hour_ttl), 'four_hour')
        if signals:
            all_signals.append(signals)
    if ('hour' in timeframes):
        signals = condense_timeframe(data, get_data('BTC_hour', hour_ttl), 'hour')
        if signals:
            all_signals.append(signals)
    if ('fifteen_minute' in timeframes):
        signals = condense_timeframe(data, get_data('BTC_fifteen_minute', fifteen_minute_ttl), 'fifteen_minute')
        if signals:
            all_signals.append(signals)
    if ('minute' in timeframes):
        signals = condense_timeframe(data, get_data('BTC_minute', minute_ttl), 'minute')
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

    if (len(all_signals) == 1):
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
            "body": json.dumps(multi_tf(all_signals, len(all_signals))),
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }

def test_combos(event, context):
    if (event['queryStringParameters'] == None):
        return {
            "statusCode": 502,
            "body": "No parameters given",
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }

    # Load the payload into a usable format
    data = json.loads(event['queryStringParameters']['data'])

    if not data:
        return {
            "statusCode": 502,
            "body": "No data given",
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }

    all_indicators = []
    all_signals = []
    
    for indicator in data:
        if 'month' in indicator:
            all_indicators.append({
                'indicator': indicator['indicator'],
                'timeframe': 'month',
                'params': indicator['month']['params']
            })

        if 'week' in indicator:
            all_indicators.append({
                'indicator': indicator['indicator'],
                'timeframe': 'week',
                'params': indicator['week']['params']
            })
        
        if 'day' in indicator:
            all_indicators.append({
                'indicator': indicator['indicator'],
                'timeframe': 'day',
                'params': indicator['day']['params']
            })

        if 'four_hour' in indicator:
            all_indicators.append({
                'indicator': indicator['indicator'],
                'timeframe': 'four_hour',
                'params': indicator['four_hour']['params']
            })

        if 'hour' in indicator:
            all_indicators.append({
                'indicator': indicator['indicator'],
                'timeframe': 'hour',
                'params': indicator['hour']['params']
            })

        if 'fifteen_minute' in indicator:
            all_indicators.append({
                'indicator': indicator['indicator'],
                'timeframe': 'fifteen_minute',
                'params': indicator['fifteen_minute']['params']
            })

        if 'minute' in indicator:
            all_indicators.append({
                'indicator': indicator['indicator'],
                'timeframe': 'minute',
                'params': indicator['minute']['params']
            })

    month_candles = get_data('BTC_month', month_ttl)
    week_candles = get_data('BTC_week', week_ttl)
    day_candles = get_data('BTC_day', day_ttl)
    four_hour_candles = get_data('BTC_four_hour', four_hour_ttl)
    hour_candles = get_data('BTC_hour', hour_ttl)
    fifteen_minute_candles = get_data('BTC_fifteen_minute', fifteen_minute_ttl)
    minute_candles = get_data('BTC_minute', minute_ttl)

    for i in range(len(all_indicators)):
        comb_list = list(combinations(all_indicators, (i+1)))
        print(len(comb_list))
        for combination in comb_list:
            combination_signals = []
            month_indicators = []
            week_indicators = []
            day_indicators = []
            four_hour_indicators = []
            hour_indicators = []
            fifteen_minute_indicators = []
            minute_indicators = []
            for item in combination:
                if item['timeframe'] == 'month': month_indicators.append(item)
                elif item['timeframe'] == 'week': week_indicators.append(item)
                elif item['timeframe'] == 'day': day_indicators.append(item)
                elif item['timeframe'] == 'four_hour': four_hour_indicators.append(item)
                elif item['timeframe'] == 'hour': hour_indicators.append(item)
                elif item['timeframe'] == 'fifteen_minute': fifteen_minute_indicators.append(item)
                elif item['timeframe'] == 'minute': minute_indicators.append(item)

            if month_indicators:
                signals = condense_timeframe(month_indicators, month_candles, 'month')
                if signals:
                    combination_signals.append(signals)
            if week_indicators:
                signals = condense_timeframe(week_indicators, week_candles, 'week')
                if signals:
                    combination_signals.append(signals)
            if day_indicators:
                signals = condense_timeframe(day_indicators, day_candles, 'day')
                if signals:
                    combination_signals.append(signals)
            if four_hour_indicators:
                signals = condense_timeframe(four_hour_indicators, four_hour_candles, 'four_hour')
                if signals:
                    combination_signals.append(signals)
            if hour_indicators:
                signals = condense_timeframe(hour_indicators, hour_candles, 'hour')
                if signals:
                    combination_signals.append(signals)
            if fifteen_minute_indicators:
                signals = condense_timeframe(fifteen_minute_indicators, fifteen_minute_candles, 'fifteen_minute')
                if signals:
                    combination_signals.append(signals)
            if minute_indicators:
                signals = condense_timeframe(minute_indicators, minute_candles, 'minute')
                if signals:
                    combination_signals.append(signals)

            if combination_signals:
                if len(combination_signals) == 1:
                    all_signals.append([combination, one_tf(combination_signals[0])])

                else:
                    all_signals.append([combination, multi_tf(combination_signals, len(combination_signals))])

                all_signals.sort(key = lambda current_signals: current_signals[1][len(current_signals[1]) - 1]['avg_roi'], reverse = True)
                all_signals[:100]

    return {
        "statusCode": 200,
        "body": json.dumps(all_signals),
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

def condense_timeframe(data, candles, timeframe):
    # Error catching for get_data
    if not candles:
        return []
    else:
        candles = pd.read_json(candles)

    timeframe_data = []
    timeframe_signals = []

    # If an indicator is requested on this timeframe,
    # append that indicator's data to an array
    for i in range(len(data)):
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
        for i in range(len(candles)):
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
    for i in range(len(all_signals)):
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
    for i in range(a_s_length):
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
def match_indicator(indicator, params, candles):
    if (indicator == 'rsi'):
        return rsi(params, candles)
    elif (indicator == 'macd'):
        return macd(candles)
    elif (indicator == 'bb'):
        return bb(candles)
    else:
        return []



# VOLUME

# Accumulation/Distribution Index
def adi():
    print('adi')

# Chaikin Money Flow
def cmf():
    print('cmf')

# Ease of Movement
def emv():
    print('emv')

# Force Index
def fi():
    print('fi')

# Negative Volume Index
def nvi():
    print('nvi')

# On-Balance Volume
def obv():
    print('obv')

# Volume-price Trend
def vpt():
    print('vpt')



# VOLATILITY

# Average True Range
def atr():
    print('atr')

# Bollinger Bands
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



# TREND

# Average Directional Movement Index
def adx():
    print('adx')

# Commodity Channel Index
def cci():
    print('cci')

# Detrended Price Oscillator
def dpo():
    print('dpo')

# Ichimoku Kinkō Hyō
def ichimoku():
    print('Ichimoku')

# KST Oscillator
def kst():
    print('kst')

# Moving Average Convergence Divergence
def macd(data):
    signals = []

    for i in range(len(data)):
        if (data['c'][i] < 6500):
            signals.append({'sig': 'buy', 'str': Decimal(.5)})
        elif (data['c'][i] > 8000):
            signals.append({'sig': 'sell', 'str': Decimal(.5)})
        else:
            signals.append({'sig': 'hold', 'str': 0})

    return signals

# Mass Index
def mi():
    print('mi')

# Parabolic Stop And Reverse
def parabolic_sar():
    print('parabolic_sar')

# Trix
def trix():
    print('trix')

# Vortex Indicator
def vi():
    print('vi')



# MOMENTUM

# Awesome Oscillator
def ao():
    print('ao')

# Kaufman's Adaptive Moving Average
def kama():
    print('kama')

# Money Flow Index
def mfi():
    print('mfi')

# Relative Strength Index
def rsi(params, candles):
    # Get the past `timeframe` rsi values in a dataframe
    rsi_total = ta.momentum.rsi(close = candles["c"], n = 14, fillna = True)
    # print('params: ', params)
    # print('rsi: ', rsi)

    signals = []

    for i in range(len(rsi_total)):
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

# Rate of Change
def roc():
    print('roc')

# Stochastic Oscillator
def sr():
    print('sr')

# True strength index
def tsi():
    print('tsi')

# Ultimate Oscillator
def uo():
    print('uo')

# Williams %R
def wr():
    print('wr')



# OTHERS

# Daily Return
def dr():
    print('dr')

# Daily Log Return
def dlr():
    print('dlr')

# Cumulative Return
def cr():
    print('cr')