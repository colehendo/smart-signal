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
    table = dynamodb.Table('BTC_day')
    index = event['iterator']['index'] + 1
    i = 0

    minute_ttl = 86400
    minute_gap = 60
    
    day_ttl = 157680000
    day_gap = 86400

    while i < 1:
        if ((time.time() % 1) < 0.1):
            timestamp = int(time.time())

            try:
                # Query the table for the last 20 rows of data.
                # TTL and gap values can easily be found in btc-populate.py
                results = table.query(
                    KeyConditionExpression = Key('s').eq('BTC') & Key('t').gt((timestamp + day_ttl) - (day_gap * 50))
                )
            except ClientError as e:
                print(e.response['Error']['Code'])
                print(e.response['ResponseMetadata']['HTTPStatusCode'])
                print(e.response['Error']['Message'])
            else:
                if 'Items' in results:
                    # Turn the returned object into a JSON string,
                    # and pass it to pandas to make it readable for TA
                    df = pd.read_json(json.dumps(results['Items']))

                    rsi = ta.momentum.rsi(close = df["c"], n = 14, fillna = True)
                    print(rsi)

                    macd = ta.trend.macd(close = df["c"], n_fast = 12, n_slow = 26, fillna = True)
                    print(macd)

                    macd_diff = ta.trend.macd_diff(close = df["c"], n_fast = 12, n_slow = 26, n_sign = 9, fillna = True)
                    print(macd_diff)

                    macd_signal = ta.trend.macd_signal(close = df["c"], n_fast = 12, n_slow = 26, n_sign = 9, fillna = True)
                    print(macd_signal)




            i += 1

    return {
        'index': index
    }
