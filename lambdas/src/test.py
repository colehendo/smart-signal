# Main cryptocompare API key: 52d6bec486eaf67f12a1462e29f2fa83b047b7ffb6c953de9e6bdc0b84ef98c8
# Backup cryptocompare API key: 2290c26ba11beff3bf85e4a7c72d6386f7e6215c710586c1996c8895387d5dc8

import json
import time
import datetime
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError
dynamodb = boto3.resource('dynamodb')

def populate(event, context):
    print("AYO ADRIAN")
    table = dynamodb.Table('BTC_second')
    i = 0

    while i < 1:
        if ((time.time() % 1) < 0.1):
            timestamp = int(time.time())

            try:
                result = table.get_item(
                    Key = {
                        's': 'BTC',
                        't': timestamp + 30
                    }
                )
            except ClientError as e:
                print(e.response['Error']['Code'])
                print(e.response['ResponseMetadata']['HTTPStatusCode'])
                print(e.response['Error']['Message'])
            else:
                if 'Item' in result:
                    return (result['Item'])
                    print("cool!")

                else:
                    print('aaahhhh fuck')

            i += 1

    return 3