import time
from decimal import Decimal
import simplejson as json
from importlib import import_module
from multiprocessing import Process, Pipe

import pandas as pd
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
dynamodb = boto3.resource('dynamodb')

timestamp = int(time.time())
balance = 100000

all_indicators = []

month_candles = []
week_candles = []
day_candles = []
four_hour_candles = []
hour_candles = []
fifteen_minute_candles = []
minute_candles = []

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
    data = json.loads(event['queryStringParameters']['data'])

    if not data:
        return {
            "statusCode": 502,
            "body": json.dumps("No data given"),
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }

    # Set the balance and remove the array of timeframes from the data
    global balance
    balance = data[-1][0]
    del data[-1]
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
    if ('month' in timeframes): month_candles = get_data('BTC_month', month_ttl, month_gap, month_datapoints)
    if ('week' in timeframes): week_candles = get_data('BTC_week', week_ttl, week_gap, week_datapoints)
    if ('day' in timeframes): day_candles = get_data('BTC_day', day_ttl, day_gap, day_datapoints)
    if ('four_hour' in timeframes): four_hour_candles = get_data('BTC_four_hour', four_hour_ttl, four_hour_gap, four_hour_datapoints)
    if ('hour' in timeframes): hour_candles = get_data('BTC_hour', hour_ttl, hour_gap, hour_datapoints)
    if ('fifteen_minute' in timeframes): fifteen_minute_candles = get_data('BTC_fifteen_minute', fifteen_minute_ttl, fifteen_minute_gap, fifteen_minute_datapoints)
    if ('minute' in timeframes): minute_candles = get_data('BTC_minute', minute_ttl, minute_gap, minute_datapoints)

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


# A simple function to call the indicators.
def match_indicator(indicator, params, candles, timeframe):
    return import_module("src.algorithms.indicators." + indicator).run(params, candles, timeframe)


def reduce_tf(all_signals, tf_signals):
    final_signals = []
    tf_sig_len = len(tf_signals)

    global balance
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
                    transaction = (round((Decimal(str_total / str_count) * Decimal(signal['price'])), 10))
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
