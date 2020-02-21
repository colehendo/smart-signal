# Main cryptocompare API key: 52d6bec486eaf67f12a1462e29f2fa83b047b7ffb6c953de9e6bdc0b84ef98c8
# Backup cryptocompare API key: 2290c26ba11beff3bf85e4a7c72d6386f7e6215c710586c1996c8895387d5dc8

import json
import time
from decimal import Decimal
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

    day_ttl = 157680000
    day_gap = 86400

    while i < 1:
        if ((time.time() % 1) < 0.1):
            timestamp = int(time.time())

            try:
                results = table.query(
                    KeyConditionExpression = Key('s').eq('BTC') & Key('t').gt((timestamp + day_ttl) - (day_gap * 21))
                )
            except ClientError as e:
                print(e.response['Error']['Code'])
                print(e.response['ResponseMetadata']['HTTPStatusCode'])
                print(e.response['Error']['Message'])
            else:
                if 'Items' in results:
                    print(results['Items'])
                    test = pd.read_json(results['Items'])
                    print(test)


            i += 1

    return {
        'index': index
    }
