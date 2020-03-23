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
    print('event: ', event)
    print('context: ', context)
    hour_ttl = 2628000
    hour_gap = 3600

    four_hour_ttl = 15768000
    four_hour_gap = 14400

    day_ttl = 157680000
    day_gap = 86400

    week_ttl = 0
    week_gap = 604800

    # Get the different rsi and macd values based on
    # the last 30 values from each table
    # return_val = rsi('BTC_hour', timestamp, hour_ttl, hour_gap, 45)
    # rsi('BTC_four_hour', timestamp, four_hour_ttl, four_hour_gap, 30)
    return_val = rsi('BTC_day', day_ttl, day_gap)
    # rsi('BTC_week', timestamp, week_ttl, week_gap, 30)

    return {
        "statusCode": 200,
        "body": json.dumps(return_val),
        "headers": {
            "Access-Control-Allow-Origin": "*"
        }
    }
 
def rsi(table, ttl, gap):
    dynamo_table = dynamodb.Table(table)
    try:
        # Query the table for the last `timeframe` rows of data.
        # TTL and gap values can easily be found in btc-populate.py
        results = dynamo_table.scan()
    except ClientError as e:
        print(e.response['Error']['Code'])
        print(e.response['ResponseMetadata']['HTTPStatusCode'])
        print(e.response['Error']['Message'])
    else:
        if 'Items' in results:
            # Turn the returned object into a JSON string,
            # and pass it to pandas to make it readable for TA
            print(results['Items'])
            df = pd.read_json(json.dumps(results['Items']))

            # Get the past `timeframe` rsi values in a dataframe
            rsi_total = ta.momentum.rsi(close = df["c"], n = 14, fillna = True)

            signals = []
            balance = 100000
            signal_total = 0

            for i in range(0, len(rsi_total)):
                print(rsi_total.iloc[i])
                current_rsi = rsi_total.iloc[i]
                if (current_rsi < 100) and (current_rsi > 0):
                    if (current_rsi < 30):
                        if (not signals) or (signals[len(signals) - 1]['signal'] != 'buy'):
                            signal_total += 1
                            strength = round(Decimal((100 - current_rsi - 10) / 100), 10)
                            transaction = round((strength * results['Items'][i]['c']), 2)
                            balance = round((balance - transaction), 2)
                            roi = round((((balance - 100000) / 100000) * 100), 4)
                            signals.append({
                                'signal': 'buy',
                                'time': results['Items'][i]['t'],
                                'price': results['Items'][i]['c'],
                                'balance': balance,
                                'strength': strength,
                                'roi': roi,
                                'avg_roi': round((roi / signal_total), 6)
                            })
                    elif (current_rsi > 70):
                        if (not signals) or (signals[len(signals) - 1]['signal'] != 'sell'):
                            signal_total += 1
                            strength = round(Decimal((current_rsi - 10) / 100), 10)
                            transaction = round((strength * results['Items'][i]['c']), 2)
                            balance = round((balance - transaction), 2)
                            roi = round((((balance - 100000) / 100000) * 100), 4)
                            signals.append({
                                'signal': 'sell',
                                'time': results['Items'][i]['t'],
                                'price': results['Items'][i]['c'],
                                'balance': balance,
                                'strength': strength,
                                'roi': roi,
                                'avg_roi': round((roi / signal_total), 6)
                            })

            print(signals)
            return signals

        else:
            return 'sorry...'

            # if (table == 'BTC_hour'):
            #     rsi(timestamp, 'rsi_hour', rsi_val, 20, 80, 30)
            # elif (table == 'BTC_four_hour'):
            #     rsi(timestamp, 'rsi_four_hour', rsi_val, 20, 80, 20)
            # elif (table == 'BTC_day'):
            #     rsi(timestamp, 'rsi_day', rsi_val, 30, 70, 10)
            # elif (table == 'BTC_week'):
            #     rsi(timestamp, 'rsi_week', rsi_val, 40, 60, 0)
            # else:
            #     return
