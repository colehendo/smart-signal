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
    index = event['iterator']['index'] + 1
    i = 0

    hour_ttl = 2628000
    hour_gap = 3600

    four_hour_ttl = 15768000
    four_hour_gap = 14400

    day_ttl = 157680000
    day_gap = 86400

    week_ttl = 0
    week_gap = 604800

    while i < 1:
        if ((time.time() % 1) < 0.1):
            timestamp = int(time.time())

            # Get the different rsi and macd values based on
            # the last 30 values from each table
            get_values('BTC_hour', timestamp, hour_ttl, hour_gap, 30)
            get_values('BTC_four_hour', timestamp, four_hour_ttl, four_hour_gap, 30)
            get_values('BTC_day', timestamp, day_ttl, day_gap, 30)
            get_values('BTC_week', timestamp, week_ttl, week_gap, 30)

            i += 1

    return {
        'index': index
    }

def get_values(table, timestamp, ttl, gap, timeframe):
    print(table)
    dynamo_table = dynamodb.Table(table)
    try:
        # Query the table for the last `timeframe` rows of data.
        # TTL and gap values can easily be found in btc-populate.py
        results = dynamo_table.query(
            KeyConditionExpression = Key('s').eq('BTC') & Key('t').gt((timestamp + ttl) - (gap * timeframe))
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

            # Get the past `timeframe` rsi values in a dataframe
            rsi = ta.momentum.rsi(close = df["c"], n = 14, fillna = True)
            for i in range(0, timeframe):
                if (rsi.iloc[i] < 100) and (rsi.iloc[i] > 0):
                    # Find the first value in the list that
                    # isn't equal to 100 or 0
                    rsi_val = rsi.iloc[i]
                    break

            # Get the past `timeframe` MACD histogram values in a dataframe
            macd_diff = ta.trend.macd_diff(close = df["c"], n_fast = 12, n_slow = 26, n_sign = 9, fillna = True)
            # The very first one is always 0. Comparing these two
            # next values allows us to see a reversal in trend
            macd_diff_new = macd_diff.iloc[1]
            macd_diff_prev = macd_diff.iloc[2]

            if (table == 'BTC_hour'):
                rsi_macd('hour', rsi_val, 20, 80, macd_diff_new, macd_diff_prev)
            elif (table == 'BTC_four_hour'):
                rsi_macd('four hour', rsi_val, 20, 80, macd_diff_new, macd_diff_prev)
            elif (table == 'BTC_day'):
                rsi_macd('day', rsi_val, 30, 70, macd_diff_new, macd_diff_prev)
            elif (table == 'BTC_week'):
                rsi_macd('week', rsi_val, 40, 60, macd_diff_new, macd_diff_prev)
            else:
                return

def rsi_macd(timeframe, rsi, rsi_buy, rsi_sell, macd_diff_new, macd_diff_prev):
    if (rsi < rsi_buy):
        print('rsi buy')
        # Going from negative to positive indicates bullish trend. Buy
        if (macd_diff_new >= 0) and (macd_diff_prev < 0):
            print('BUY BUY BUY: ', timeframe)
            print('rsi: ', rsi)
            print('macd new: ', macd_diff_new, ' macd prev: ', macd_diff_prev)
        else:
            return

    elif (rsi > rsi_sell):
        print('rsi sell')
        # Going from positive to negative indicates bearish trend. Sell
        if (macd_diff_new <= 0) and (macd_diff_prev > 0):
            print('SELL SELL SELL: ', timeframe)
            print('rsi: ', rsi)
            print('macd new: ', macd_diff_new, ' macd prev: ', macd_diff_prev)
        else:
            return

    else:
        return
