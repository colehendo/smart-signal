# Main cryptocompare API key: 52d6bec486eaf67f12a1462e29f2fa83b047b7ffb6c953de9e6bdc0b84ef98c8
# Backup cryptocompare API key: 2290c26ba11beff3bf85e4a7c72d6386f7e6215c710586c1996c8895387d5dc8

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

    test_payload = ['day', 'rsi', 'macd', 'bb']

    # Get the different rsi and macd values based on
    # the last 30 values from each table
    # return_val = rsi('BTC_hour', timestamp, hour_ttl, hour_gap, 45)
    # rsi('BTC_four_hour', timestamp, four_hour_ttl, four_hour_gap, 30)
    # return_val = rsi('BTC_day')
    # rsi('BTC_week', timestamp, week_ttl, week_gap, 30)

    data = get_data(test_payload[0])

    all_signals = []
    final_signals = []
    balance = 100000
    strength = 0
    total_roi = 0
    roi_count = 0

    for i in range(1, len(test_payload)):
        all_signals.append(match_indicator(test_payload[i], data))

    a_s_length = len(all_signals)

    for i in range (0, len(data)):
        signal = all_signals[0][i]['sig']
        if (signal != 'hold' and ((not final_signals) or (signal != final_signals[len(final_signals) - 1]['sig']))):
            strength += all_signals[0][i]['str']
            for j in range (1, a_s_length):
                if (all_signals[j][i]['sig'] != signal):
                    break
                elif (j == (a_s_length - 1)):
                    final_strength = round((strength / a_s_length), 10)
                    transaction = round((final_strength * round(Decimal(data['c'][i]), 6)), 2)
                    roi = round((((balance - 100000) / 100000) * 100), 4)
                    if (signal == 'buy'):
                        balance = round((balance - transaction), 2)
                    else:
                        balance = round((balance + transaction), 2)
                        if (final_signals):
                            total_roi += roi
                            roi_count += 1

                    final_signals.append({
                        'sig': signal,
                        'time': int(data['t'][i]),
                        'amt': transaction,
                        'roi': roi
                    })
                    break
                else:
                    strength += all_signals[j][i]['str']


    final_signals.append({
        'bal': balance,
        'avg_roi': round((total_roi / roi_count, 6)
    })

    return {
        "statusCode": 200,
        "body": json.dumps(final_signals),
        "headers": {
            "Access-Control-Allow-Origin": "*"
        }
    }

def get_data(timeframe):
    table = 'BTC_second'
    if (timeframe == 'minute'):
        table = 'BTC_minute'
    elif (timeframe == 'fifteen_minute'):
        table = 'BTC_fifteen_minute'
    elif (timeframe == 'hour'):
        table = 'BTC_hour'
    elif (timeframe == 'four_hour'):
        table = 'BTC_four_hour'
    elif (timeframe == 'day'):
        table = 'BTC_day'
    elif (timeframe == 'week'):
        table = 'BTC_week'
    elif (timeframe == 'month'):
        table = 'BTC_month'

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


