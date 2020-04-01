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
    data = json.loads(event['queryStringParameters']['vals'])
    timeframes = data[0]
    data.pop(0)

    all_signals = []
    a_s_record = []

    if ('month' in timeframes):
        all_signals.append(condense_timeframe(data, get_data('BTC_month'), 'month'))
    if ('week' in timeframes):
        all_signals.append(condense_timeframe(data, get_data('BTC_week'), 'week'))
    if ('day' in timeframes):
        all_signals.append(condense_timeframe(data, get_data('BTC_day'), 'day'))
    if ('four_hour' in timeframes):
        all_signals.append(condense_timeframe(data, get_data('BTC_four_hour'), 'four_hour'))
    if ('hour' in timeframes):
        all_signals.append(condense_timeframe(data, get_data('BTC_hour'), 'hour'))
    if ('fifteen_minute' in timeframes):
        all_signals.append(condense_timeframe(data, get_data('BTC_fifteen_minute'), 'fifteen_minute'))
    if ('minute' in timeframes):
        all_signals.append(condense_timeframe(data, get_data('BTC_minute'), 'minute'))
    if ('second' in timeframes):
        all_signals.append(condense_timeframe(data, get_data('BTC_second'), 'second'))

    a_s_length = len(all_signals)
    final_signals = []

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

    for i in range(0, a_s_length):
        a_s_record.append([0, len(all_signals[i])])

    while (a_s_record[0][0] < a_s_record[0][1]):
        signal = all_signals[0][a_s_record[0][0]]
        if (signal == 'hold' or ((final_signals) and (signal == final_signals[len(final_signals) - 1]['sig']))):
            a_s_record[0][0] += 1
            continue

        if ((a_s_record[tf - 1][0] + 1) < a_s_record[tf - 1][1]):
            # If current timeframe's first signal is past its parent's next signal, send signal
            prev_too_early = all_signals[tf][0]['time'] >= all_signals[tf - 1][a_s_record[tf - 1][0] + 1]['time']
            # If current signal is past its parent's next signal
            current_too_late = all_signals[tf][a_s_record[tf][0]]['time'] >= all_signals[tf - 1][a_s_record[tf - 1][0] + 1]['time']

            if (prev_too_early):
                final_strength = round((strength / str_count), 10)
                transaction = round((final_strength * round(Decimal(all_signals[tf][a_s_record[tf][0]]['price']), 6)), 2)
                if (signal == 'buy'):
                    balance = round((balance - transaction), 2)
                    prev_buy = transaction
                    final_signals.append({
                        'sig': signal,
                        'time': int(data['t'][i]),
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
                        'time': int(data['t'][i]),
                        'amt': transaction,
                        'roi': roi
                    })
                a_s_record[0][0] += 1
                continue

            elif (current_too_late):
                tf -= 1
                a_s_record[tf][0] += 1
                continue

            if (prev_too_early or (current_too_late and (tf == 0))):
                tf = 1
                signal = all_signals[0][a_s_record[0][0]]['sig']
                strength = all_signals[0][a_s_record[0][0]]['str']
                str_count = 1
                timestamp = all_signals[0][a_s_record[0][0]]['time']

        # If its the right signal
        if (all_signals[tf][a_s_record[tf][0]]['sig'] == signal):
            # If the signal's timestamp is >= than that of its parent
            sig_past_parent = all_signals[tf][a_s_record[tf][0]]['time'] >= all_signals[tf - 1][a_s_record[tf - 1][0]]['time']
            next_sig_past_parent = all_signals[tf][a_s_record[tf][0] + 1]['time'] > all_signals[tf - 1][a_s_record[tf - 1][0]]['time']
            if (sig_past_parent or next_sig_past_parent):
                if (sig_past_parent):
                    timestamp = all_signals[tf][a_s_record[tf][0]]['time']
                if (tf == (a_s_length - 1)):
                    final_strength = round((strength / str_count), 10)
                    transaction = round((final_strength * round(Decimal(all_signals[tf][a_s_record[tf][0]]['price']), 6)), 2)
                    if (signal == 'buy'):
                        balance = round((balance - transaction), 2)
                        prev_buy = transaction
                        final_signals.append({
                            'sig': signal,
                            'time': int(data['t'][i]),
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
                            'time': int(data['t'][i]),
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


    if (roi_count == 0):
        final_signals.append({'bal': balance})
    else:
        final_signals.append({
            'bal': balance,
            'avg_roi': round(total_roi / roi_count, 6)
        })

    return {
        "statusCode": 200,
        "body": json.dumps(final_signals),
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
            return pd.read_json(json.dumps(results['Items']))
        else:
            return False

def condense_timeframe(data, candles, timeframe):
    timeframe_data = []
    timeframe_signals = []
    strength = 0

    # If an indicator is requested on this timeframe,
    # append that indicator data to an array
    for i in range(0, len(data)):
        if (data[i]['timeframe'] == timeframe):
            timeframe_data.append(match_indicator(data[i]['indicator'], candles))

    t_d_length = len(timeframe_data)

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

def match_indicator(indicator, data):
    if (indicator == 'rsi'):
        return rsi(data)
    elif (indicator == 'macd'):
        return macd(data)
    elif (indicator == 'bb'):
        return bb(data)
    else:
        return False

def rsi(data):
    # Get the past `timeframe` rsi values in a dataframe
    rsi_total = ta.momentum.rsi(close = data["c"], n = 14, fillna = True)

    signals = []

    for i in range(0, len(rsi_total)):
        current_rsi = rsi_total.iloc[i]
        if (current_rsi < 100) and (current_rsi > 0):
            if (current_rsi < 30):
                signals.append({'sig': 'buy', 'str': round(Decimal((100 - current_rsi - 10) / 100), 10)})
            elif (current_rsi > 70):
                signals.append({'sig': 'sell', 'str': round(Decimal((current_rsi - 10) / 100), 10)})
            else:
                signals.append({'sig': 'hold', 'str': 0})
        else:
            signals.append({'sig': 'hold', 'str': 0})

    return signals

def macd(data):
    signals = []

    for i in range(0, len(data)):
        if (data['c'][i] < 8000):
            signals.append({'sig': 'buy', 'str': Decimal(.5)})
        elif (data['c'][i] > 8000):
            signals.append({'sig': 'sell', 'str': Decimal(.5)})
        else:
            signals.append({'sig': 'hold', 'str': 0})

    return signals

def bb(data):
    signals = []

    for i in range(0, len(data)):
        if (data['c'][i] < data['o'][i]):
            signals.append({'sig': 'buy', 'str': Decimal(.5)})
        elif (data['c'][i] > data['o'][i]):
            signals.append({'sig': 'sell', 'str': Decimal(.5)})
        else:
            signals.append({'sig': 'hold', 'str': 0})

    return signals


