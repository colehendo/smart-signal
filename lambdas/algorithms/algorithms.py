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
    table = dynamodb.Table('BTC_minute')
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
                    KeyConditionExpression = Key('s').eq('BTC') & Key('t').gt((timestamp + minute_ttl) - (minute_gap * 20))
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

                    # How to access specific items in a row,
                    for index, row in df.iterrows():
                        # print each row
                        print(row)
                        # print specific items from each row
                        print(row['s'], row['t'], row['c'])

                    # How to access specific items in specific rows
                    for index in df.iterrows():
                        if (index == 4):
                            print('specific item:')
                            print(row['h'])
                            for row in index:
                                print('specific row:')
                                print(row)

                    # How to access specific items in a row
                    for index, column in df.items():
                        # print each column with each row indexed
                        print(column)
                        # print each row value for a specific column
                        if (index == 'o'):
                            print('specific column...')
                            print(column)

                    # How to access specific rows by timestamp,
                    # returning the whole row
                    access_rows = df.loc[(timestamp - (timestamp % minute_gap))]
                    print(access_rows)

                    # How to access specific rows by index,
                    # returning the whole row
                    for index in range(0, 20):
                        print(df.iloc[index])
                        # another way to access a specific item in a row
                        print(df.iloc[index]['c'])

                    # How to access columns, returning the
                    # values of those columns from each row
                    access_columns = df[['s', 't', 'c']]
                    print(access_columns)

                    # Run rsi with rows containing empty values
                    rsi_test_noNa = ta.momentum.rsi(close = df["c"], n = 14, fillna = False)
                    print(rsi_test_noNa)

                    # Run rsi without rows containing empty values
                    rsi_test_na = ta.momentum.rsi(close = df["c"], n = 14, fillna = True)
                    print(rsi_test_na)

                    # Delete any rows containing null values
                    df = ta.utils.dropna(df)


            i += 1

    return {
        'index': index
    }
