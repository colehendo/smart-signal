import time
from decimal import Decimal
import simplejson as json
from importlib import import_module
from itertools import combinations
from multiprocessing import Process, Pipe

import pandas as pd
import ta

import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
dynamodb = boto3.resource('dynamodb')

all_indicators = []
combo_results = []

month_candles_for_combos = []
week_candles_for_combos = []
day_candles_for_combos = []
four_hour_candles_for_combos = []
hour_candles_for_combos = []
fifteen_minute_candles_for_combos = []
minute_candles_for_combos = []

timestamp = int(time.time())

month_ttl = 0
month_gap = 2628000
month_datapoints = 0

week_ttl = 0
week_gap = 604800
week_datapoints = 0

day_ttl = 157680000
day_gap = 86400
day_datapoints = 1825

four_hour_ttl = 15768000
four_hour_gap = 14400
four_hour_datapoints = 1095

hour_ttl = 2628000
hour_gap = 3600
hour_datapoints = 730

fifteen_minute_ttl = 604800
fifteen_minute_gap = 900
fifteen_minute_datapoints = 672

minute_ttl = 86400
minute_gap = 60
minute_datapoints = 1440

def handler(event, context):
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
    print('data: ', data)

    if not data:
        return {
            "statusCode": 502,
            "body": "No data given",
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }

    global all_indicators
    
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

    global month_candles_for_combos
    month_candles_for_combos = get_data('BTC_month', month_ttl, month_gap, month_datapoints)
    global week_candles_for_combos
    week_candles_for_combos = get_data('BTC_week', week_ttl, week_gap, week_datapoints)
    global day_candles_for_combos
    day_candles_for_combos = get_data('BTC_day', day_ttl, day_gap, day_datapoints)
    global four_hour_candles_for_combos
    four_hour_candles_for_combos = get_data('BTC_four_hour', four_hour_ttl, four_hour_gap, four_hour_datapoints)
    global hour_candles_for_combos
    hour_candles_for_combos = get_data('BTC_hour', hour_ttl, hour_gap, hour_datapoints) 
    global fifteen_minute_candles_for_combos
    fifteen_minute_candles_for_combos = get_data('BTC_fifteen_minute', fifteen_minute_ttl, fifteen_minute_gap, fifteen_minute_datapoints)
    global minute_candles_for_combos
    minute_candles_for_combos = get_data('BTC_minute', minute_ttl, minute_gap, minute_datapoints)

    processes = []
    parent_connections = []

    for i in range(len(all_indicators)):
        parent_connection, child_connection = Pipe()
        processes.append(Process(target=calculate_combinations, args=((i + 1), child_connection)))
        parent_connections.append(parent_connection)
        processes[-1].start()
    
    for j in processes:
        j.join()

    bottom_roi = 0
    global combo_results

    for parent_connection in parent_connections:
        child_result = parent_connection.recv()[0]
        for result in child_result:
            # print('result: ', result)
            # print('len combo results: ', len(combo_results))
            # print('combo results: ', combo_results)
            if len(combo_results) < 20:
                combo_results.append(result)
            else:
                if result[1][-1]['avg_roi'] > bottom_roi:
                    combo_results.append(result)
                    combo_results.sort(key = lambda data: data[1][-1]['avg_roi'], reverse = True)
                    del combo_results[-1]
                    bottom_roi = combo_results[-1][1][-1]['avg_roi']
                    # print('bottom roi: ', bottom_roi, ' from data: ', combo_results[-1][1][-1]['avg_roi'])


    return {
        "statusCode": 200,
        "body": json.dumps(combo_results),
        "headers": {
            "Access-Control-Allow-Origin": "*"
        }
    }


def calculate_combinations(count, connection):
    combos = list(combinations(all_indicators, count))
    results = []
    processes = []
    parent_connections = []

    for combination in combos:
        parent_connection, child_connection = Pipe()
        processes.append(Process(target=run_combinations, args=(combination, child_connection)))
        parent_connections.append(parent_connection)
        processes[-1].start()

    for j in processes:
        j.join()

    for parent_connection in parent_connections:
        result = parent_connection.recv()
        if result:
            if result[1][-1]['avg_roi'] > 10:
                results.append(result)

    # for combination in combos:
    #     result = run_combinations(combination)
    #     if result:
    #         if result[1][-1]['avg_roi'] > 10:
    #             results.append(result)

    results.sort(key = lambda data: data[1][-1]['avg_roi'], reverse = True)
    if len(results) > 20:
        results = results[:20]
    connection.send([results])


# def run_combinations(combination, connection):
def run_combinations(combination, connection):
    timeframe_data = []

    combination_signals = []
    # month_indicators = []
    # week_indicators = []
    # day_indicators = []
    # four_hour_indicators = []
    # hour_indicators = []
    # fifteen_minute_indicators = []
    # minute_indicators = []
    for item in combination:
        # if item['timeframe'] == 'month': month_indicators.append(item)
        # elif item['timeframe'] == 'week': week_indicators.append(item)
        # elif item['timeframe'] == 'day': day_indicators.append(item)
        # elif item['timeframe'] == 'four_hour': four_hour_indicators.append(item)
        # elif item['timeframe'] == 'hour': hour_indicators.append(item)
        # elif item['timeframe'] == 'fifteen_minute': fifteen_minute_indicators.append(item)
        # elif item['timeframe'] == 'minute': minute_indicators.append(item)

        timeframe = item['timeframe']
        indicator = item['indicator']
        if timeframe == 'month': candles = month_candles_for_combos
        elif timeframe == 'week': candles = week_candles_for_combos
        elif timeframe == 'day': candles = day_candles_for_combos
        elif timeframe == 'four_hour': candles = four_hour_candles_for_combos
        elif timeframe == 'hour': candles = hour_candles_for_combos
        elif timeframe == 'fifteen_minute': candles = fifteen_minute_candles_for_combos
        elif timeframe == 'minute': candles = minute_candles_for_combos

        indicator_data = match_indicator(indicator, item['params'], candles, timeframe)
        if indicator_data:
            timeframe_data.append({
                'indicator': indicator,
                'tf': timeframe,
                'sig': 'hold',
                'str': 0,
                'start': candles['t'][0]
            })
            for indicator in indicator_data:
                combination_signals.append(indicator)

    # if month_indicators:
    #     signals = condense_timeframe(month_indicators, month_candles_for_combos, 'month')
    #     if signals:
    #         timeframe_data.append({
    #             'tf': 'month',
    #             'sig': 'hold',
    #             'str': 0,
    #             'start': month_candles_for_combos['t'][0]
    #         })
    #         # combination_signals.append(signals)
    #         for signal in signals:
    #             combination_signals.append(signal)
    # if week_indicators:
    #     signals = condense_timeframe(week_indicators, week_candles_for_combos, 'week')
    #     if signals:
    #         timeframe_data.append({
    #             'tf': 'week',
    #             'sig': 'hold',
    #             'str': 0,
    #             'start': week_candles_for_combos['t'][0]
    #         })
    #         # combination_signals.append(signals)
    #         for signal in signals:
    #             combination_signals.append(signal)
    # if day_indicators:
    #     signals = condense_timeframe(day_indicators, day_candles_for_combos, 'day')
    #     if signals:
    #         timeframe_data.append({
    #             'tf': 'day',
    #             'sig': 'hold',
    #             'str': 0,
    #             'start': day_candles_for_combos['t'][0]
    #         })
    #         # combination_signals.append(signals)
    #         for signal in signals:
    #             combination_signals.append(signal)
    # if four_hour_indicators:
    #     signals = condense_timeframe(four_hour_indicators, four_hour_candles_for_combos, 'four_hour')
    #     if signals:
    #         timeframe_data.append({
    #             'tf': 'four_hour',
    #             'sig': 'hold',
    #             'str': 0,
    #             'start': four_hour_candles_for_combos['t'][0]
    #         })
    #         # combination_signals.append(signals)
    #         for signal in signals:
    #             combination_signals.append(signal)
    # if hour_indicators:
    #     signals = condense_timeframe(hour_indicators, hour_candles_for_combos, 'hour')
    #     if signals:
    #         timeframe_data.append({
    #             'tf': 'hour',
    #             'sig': 'hold',
    #             'str': 0,
    #             'start': hour_candles_for_combos['t'][0]
    #         })
    #         # combination_signals.append(signals)
    #         for signal in signals:
    #             combination_signals.append(signal)
    # if fifteen_minute_indicators:
    #     signals = condense_timeframe(fifteen_minute_indicators, fifteen_minute_candles_for_combos, 'fifteen_minute')
    #     if signals:
    #         timeframe_data.append({
    #             'tf': 'fifteen_minute',
    #             'sig': 'hold',
    #             'str': 0,
    #             'start': fifteen_minute_candles_for_combos['t'][0]
    #         })
    #         # combination_signals.append(signals)
    #         for signal in signals:
    #             combination_signals.append(signal)
    # if minute_indicators:
    #     signals = condense_timeframe(minute_indicators, minute_candles_for_combos, 'minute')
    #     if signals:
    #         timeframe_data.append({
    #             'tf': 'minute',
    #             'sig': 'hold',
    #             'str': 0,
    #             'start': minute_candles_for_combos['t'][0]
    #         })
    #         # combination_signals.append(signals)
    #         for signal in signals:
    #             combination_signals.append(signal)

    if combination_signals:
        combination_signals.sort(key = lambda signal: signal['time'])
        # return ([combination, any_tf(combination_signals, timeframe_data)])
        connection.send([combination, any_tf(combination_signals, timeframe_data)])

    else:
        # return []
        connection.send([])


def get_data(table, ttl, gap, datapoints):
    dynamo_table = dynamodb.Table(table)
    try:
        # Scan the table for all datapoints
        if datapoints > 0:
            results = dynamo_table.query(
                KeyConditionExpression = Key('s').eq('BTC') & Key('t').gt((timestamp + ttl) - (gap * datapoints))
            )
        else:
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
            return pd.read_json(json.dumps(results['Items']))
        else:
            return []


def condense_timeframe(all_data, candles, timeframe):
    # Error catching for get_data
    if candles.empty:
        return []

    timeframe_data = []
    timeframe_signals = []
    signal_records = []

    # If an indicator is requested on this timeframe,
    # append that indicator's data to an array
    for data in all_data:
        if (data['timeframe'] == timeframe):
            indicator_data = match_indicator(data['indicator'], data['params'], candles, timeframe)
            if indicator_data:
                signal_records.append({
                    'indicator': data['indicator'],
                    'sig': 'hold',
                    'str': 0
                })
                for indicator in indicator_data:
                    timeframe_data.append(indicator)

    # Error catching for no signals returned
    if not timeframe_data:
        return []

    timeframe_data.sort(key = lambda data: data['time'])

    overall_sig = 'hold'
    s_r_length = len(signal_records)

    # Go through each indicator's signal at a given index.
    # If all signals match at one index, calculate the avg
    # strength of all those signals and append it to a final array
    if (s_r_length > 1):
        for signal in timeframe_data:
            current_sig = signal['sig']
            current_indicator = signal['indicator']
            if current_sig != overall_sig:
                str_count = 0
                str_total = 0
                for i in range(s_r_length):
                    if current_indicator == signal_records[i]['indicator']:
                        if current_sig != signal_records[i]['sig']:
                            signal_records[i]['sig'] = current_sig
                            signal_records[i]['str'] = signal['str']
                            str_total += signal['str']
                            str_count += 1
                    else:
                        if current_sig != signal_records[i]['sig']:
                            break
                        elif signal_records[i]['str'] != 0:
                            str_total += signal_records[i]['str']
                            str_count += 1

                    if i == (s_r_length - 1):
                        overall_sig = current_sig
                        signal['str'] = round(Decimal(str_total / str_count), 10)
                        timeframe_signals.append(signal)

    else:
        timeframe_signals = timeframe_data

    timeframe_signals.sort(key = lambda data: data['time'])

    return timeframe_signals


def any_tf(all_signals, tf_signals):
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
                # if current_tf == tf_signals[i]['tf']:
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
    return import_module("src.algorithms.indicators." + indicator).run(params, candles, timeframe)