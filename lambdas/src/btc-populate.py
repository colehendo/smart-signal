import json
import time
import datetime
import threading
from decimal import Decimal
import requests

import boto3
from botocore.exceptions import ClientError
dynamodb = boto3.resource('dynamodb')

def populate(event, context):
    table = dynamodb.Table('BTC_second_free')
    i = 0

    while i < 60:
        if ((time.time() % 1) == 0):
            timestamp = int(time.time())
            btc = requests.get('https://api.coinbase.com/v2/prices/BTC-USD/spot')
            price = Decimal(btc.json()["data"]["amount"])

            minute(timestamp, price)
            fifteen_minute(timestamp, price)
            hour(timestamp, price)
            four_hour(timestamp, price)
            day(timestamp, price)
            week(timestamp, price)
            month(timestamp, price)

            item = {
                's': 'BTC',
                't': timestamp + 60,
                'p': price
            }

            table.put_item(Item = item)
            
            i += 1

    body = {
        "message": "Table updated successfully",
        "item": item
    }

    response = {
        "statusCode": 200,
        "body": body
    }

    return response

def minute(timestamp, price):
    table = dynamodb.Table('BTC_minute_free')

    if ((timestamp % 60) == 0):
        item = {
            's': 'BTC',
            't': timestamp + 86400,
            'h': price,
            'l': price,
            'o': price,
            'c': price,
        }

        table.put_item(Item = item)

        try:
            result = table.get_item(
                Key = {
                    's': 'BTC',
                    't': ((timestamp + 86400) - 60)
                }
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            if 'Item' in result:
                volume_api = requests.get('https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=1&api_key=52d6bec486eaf67f12a1462e29f2fa83b047b7ffb6c953de9e6bdc0b84ef98c8')
                expressionAttributeValues = {
                    ':x': 0,
                    ':v': Decimal(str(volume_api.json()["Data"]["Data"][0]["volumeto"]))
                }
                if ((result['Item']['c'] - result['Item']['o']) != 0):
                    print('UPDATING')
                    expressionAttributeValues.update({':x': round((((result['Item']['c'] - result['Item']['o']) / result['Item']['o']) * 100), 10)})

                update_result = table.update_item(
                    Key = {
                        's': 'BTC',
                        't': ((timestamp + 86400) - 60)
                    },
                    UpdateExpression = "set x = :x, v = :v",
                    ExpressionAttributeValues = expressionAttributeValues,
                    ReturnValues="UPDATED_NEW"
                )

    else:
        try:
            result = table.get_item(
                Key = {
                    's': 'BTC',
                    't': ((timestamp + 86400) - (timestamp % 60))
                }
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            if 'Item' in result:
                key = {
                    's': 'BTC',
                    't': ((timestamp + 86400) - (timestamp % 60))
                }
                updateExpression = "set c = :c"
                expressionAttributeValues = {
                    ':c': price
                }

                if (result['Item']['h'] < price):
                    updateExpression = "set c = :c, h = :h"
                    expressionAttributeValues.update({':h': price})

                if (result['Item']['l'] > price):
                    updateExpression = "set c = :c, l = :l"
                    expressionAttributeValues.update({':l': price})

                if ((result['Item']['h'] < price) and (result['Item']['l'] > price)):
                    updateExpression = "set c = :c, h = :h, l = :l"

                update_result = table.update_item(
                    Key = key,
                    UpdateExpression = updateExpression,
                    ExpressionAttributeValues = expressionAttributeValues,
                    ReturnValues = "UPDATED_NEW"
                )

def fifteen_minute(timestamp, price):
    table = dynamodb.Table('BTC_fifteen_minute_free')     

    if ((timestamp % 900) == 0):
        item = {
            's': 'BTC',
            't': timestamp + 604800,
            'h': price,
            'l': price,
            'o': price,
            'c': price,
        }

        table.put_item(Item = item)

        try:
            result = table.get_item(
                Key = {
                    's': 'BTC',
                    't': ((timestamp + 604800) - 900)
                }
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            if 'Item' in result:
                volume_api = requests.get('https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=15&api_key=52d6bec486eaf67f12a1462e29f2fa83b047b7ffb6c953de9e6bdc0b84ef98c8')
                data = volume_api.json()["Data"]["Data"]
                volume = 0
                for i in range(0, 15):
                    volume += data[i]["volumeto"]

                expressionAttributeValues = {
                    ':x': 0,
                    ':v': Decimal(str(volume))
                }
                if ((result['Item']['c'] - result['Item']['o']) != 0):
                    expressionAttributeValues.update({':x': round((((result['Item']['c'] - result['Item']['o']) / result['Item']['o']) * 100), 10)})

                update_result = table.update_item(
                    Key = {
                        's': 'BTC',
                        't': ((timestamp + 604800) - 900)
                    },
                    UpdateExpression = "set x = :x, v = :v",
                    ExpressionAttributeValues = expressionAttributeValues,
                    ReturnValues="UPDATED_NEW"
                )

    else:
        try:
            result = table.get_item(
                Key = {
                    's': 'BTC',
                    't': ((timestamp + 604800) - (timestamp % 900))
                }
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            if 'Item' in result:
                key = {
                    's': 'BTC',
                    't': ((timestamp + 604800) - (timestamp % 900))
                }
                updateExpression = "set c = :c"
                expressionAttributeValues = {
                    ':c': price
                }

                if (result['Item']['h'] < price):
                    updateExpression = "set c = :c, h = :h"
                    expressionAttributeValues.update({':h': price})

                if (result['Item']['l'] > price):
                    updateExpression = "set c = :c, l = :l"
                    expressionAttributeValues.update({':l': price})

                if ((result['Item']['h'] < price) and (result['Item']['l'] > price)):
                    updateExpression = "set c = :c, h = :h, l = :l"

                update_result = table.update_item(
                    Key = key,
                    UpdateExpression = updateExpression,
                    ExpressionAttributeValues = expressionAttributeValues,
                    ReturnValues = "UPDATED_NEW"
                )

def hour(timestamp, price):
    table = dynamodb.Table('BTC_hour_free')     

    if ((timestamp % 3600) == 0):
        item = {
            's': 'BTC',
            't': timestamp + 2628000,
            'h': price,
            'l': price,
            'o': price,
            'c': price,
        }

        table.put_item(Item = item)

        try:
            result = table.get_item(
                Key = {
                    's': 'BTC',
                    't': ((timestamp + 2628000) - 3600)
                }
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            if 'Item' in result:
                volume_api = requests.get('https://min-api.cryptocompare.com/data/v2/histohour?fsym=BTC&tsym=USD&limit=1&api_key=52d6bec486eaf67f12a1462e29f2fa83b047b7ffb6c953de9e6bdc0b84ef98c8')
                expressionAttributeValues = {
                    ':x': 0,
                    ':v': Decimal(str(volume_api.json()["Data"]["Data"][0]["volumeto"]))
                }
                if ((result['Item']['c'] - result['Item']['o']) != 0):
                    expressionAttributeValues.update({':x': round((((result['Item']['c'] - result['Item']['o']) / result['Item']['o']) * 100), 10)})

                update_result = table.update_item(
                    Key = {
                        's': 'BTC',
                        't': ((timestamp + 2628000) - 3600)
                    },
                    UpdateExpression = "set x = :x, v = :v",
                    ExpressionAttributeValues = expressionAttributeValues,
                    ReturnValues="UPDATED_NEW"
                )

    else:
        try:
            result = table.get_item(
                Key = {
                    's': 'BTC',
                    't': ((timestamp + 2628000) - (timestamp % 3600))
                }
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            if 'Item' in result:
                key = {
                    's': 'BTC',
                    't': ((timestamp + 2628000) - (timestamp % 3600))
                }
                updateExpression = "set c = :c"
                expressionAttributeValues = {
                    ':c': price
                }

                if (result['Item']['h'] < price):
                    updateExpression = "set c = :c, h = :h"
                    expressionAttributeValues.update({':h': price})

                if (result['Item']['l'] > price):
                    updateExpression = "set c = :c, l = :l"
                    expressionAttributeValues.update({':l': price})

                if ((result['Item']['h'] < price) and (result['Item']['l'] > price)):
                    updateExpression = "set c = :c, h = :h, l = :l"

                update_result = table.update_item(
                    Key = key,
                    UpdateExpression = updateExpression,
                    ExpressionAttributeValues = expressionAttributeValues,
                    ReturnValues = "UPDATED_NEW"
                )

def four_hour(timestamp, price):
    table = dynamodb.Table('BTC_four_hour_free')     

    if ((timestamp % 14400) == 0):
        item = {
            's': 'BTC',
            't': timestamp + 15768000,
            'h': price,
            'l': price,
            'o': price,
            'c': price,
        }

        table.put_item(Item = item)

        try:
            result = table.get_item(
                Key = {
                    's': 'BTC',
                    't': ((timestamp + 15768000) - 14400)
                }
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            if 'Item' in result:
                volume_api = requests.get('https://min-api.cryptocompare.com/data/v2/histohour?fsym=BTC&tsym=USD&limit=4&api_key=52d6bec486eaf67f12a1462e29f2fa83b047b7ffb6c953de9e6bdc0b84ef98c8')
                data = volume_api.json()["Data"]["Data"]
                volume = 0
                for i in range(0, 4):
                    volume += data[i]["volumeto"]

                expressionAttributeValues = {
                    ':x': 0,
                    ':v': Decimal(str(volume))
                }
                if ((result['Item']['c'] - result['Item']['o']) != 0):
                    expressionAttributeValues.update({':x': round((((result['Item']['c'] - result['Item']['o']) / result['Item']['o']) * 100), 10)})

                update_result = table.update_item(
                    Key = {
                        's': 'BTC',
                        't': ((timestamp + 15768000) - 14400)
                    },
                    UpdateExpression = "set x = :x, v = :v",
                    ExpressionAttributeValues = expressionAttributeValues,
                    ReturnValues="UPDATED_NEW"
                )

    else:
        try:
            result = table.get_item(
                Key = {
                    's': 'BTC',
                    't': ((timestamp + 15768000) - (timestamp % 14400))
                }
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            if 'Item' in result:
                key = {
                    's': 'BTC',
                    't': ((timestamp + 15768000) - (timestamp % 14400))
                }
                updateExpression = "set c = :c"
                expressionAttributeValues = {
                    ':c': price
                }

                if (result['Item']['h'] < price):
                    updateExpression = "set c = :c, h = :h"
                    expressionAttributeValues.update({':h': price})

                if (result['Item']['l'] > price):
                    updateExpression = "set c = :c, l = :l"
                    expressionAttributeValues.update({':l': price})

                if ((result['Item']['h'] < price) and (result['Item']['l'] > price)):
                    updateExpression = "set c = :c, h = :h, l = :l"

                update_result = table.update_item(
                    Key = key,
                    UpdateExpression = updateExpression,
                    ExpressionAttributeValues = expressionAttributeValues,
                    ReturnValues = "UPDATED_NEW"
                )

def day(timestamp, price):
    table = dynamodb.Table('BTC_day_free')     

    if ((timestamp % 86400) == 0):
        item = {
            's': 'BTC',
            't': timestamp + 157680000,
            'h': price,
            'l': price,
            'o': price,
            'c': price,
        }

        table.put_item(Item = item)

        try:
            result = table.get_item(
                Key = {
                    's': 'BTC',
                    't': ((timestamp + 157680000) - 86400)
                }
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            if 'Item' in result:
                volume_api = requests.get('https://min-api.cryptocompare.com/data/v2/histoday?fsym=BTC&tsym=USD&limit=1&api_key=52d6bec486eaf67f12a1462e29f2fa83b047b7ffb6c953de9e6bdc0b84ef98c8')
                expressionAttributeValues = {
                    ':x': 0,
                    ':v': Decimal(str(volume_api.json()["Data"]["Data"][0]["volumeto"]))
                }
                if ((result['Item']['c'] - result['Item']['o']) != 0):
                    expressionAttributeValues.update({':x': round((((result['Item']['c'] - result['Item']['o']) / result['Item']['o']) * 100), 10)})

                update_result = table.update_item(
                    Key = {
                        's': 'BTC',
                        't': ((timestamp + 157680000) - 86400)
                    },
                    UpdateExpression = "set x = :x, v = :v",
                    ExpressionAttributeValues = expressionAttributeValues,
                    ReturnValues="UPDATED_NEW"
                )

    else:
        try:
            result = table.get_item(
                Key = {
                    's': 'BTC',
                    't': ((timestamp + 157680000) - (timestamp % 86400))
                }
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            if 'Item' in result:
                key = {
                    's': 'BTC',
                    't': ((timestamp + 157680000) - (timestamp % 86400))
                }
                updateExpression = "set c = :c"
                expressionAttributeValues = {
                    ':c': price
                }

                if (result['Item']['h'] < price):
                    updateExpression = "set c = :c, h = :h"
                    expressionAttributeValues.update({':h': price})

                if (result['Item']['l'] > price):
                    updateExpression = "set c = :c, l = :l"
                    expressionAttributeValues.update({':l': price})

                if ((result['Item']['h'] < price) and (result['Item']['l'] > price)):
                    updateExpression = "set c = :c, h = :h, l = :l"

                update_result = table.update_item(
                    Key = key,
                    UpdateExpression = updateExpression,
                    ExpressionAttributeValues = expressionAttributeValues,
                    ReturnValues = "UPDATED_NEW"
                )

def week(timestamp, price):
    table = dynamodb.Table('BTC_week_free')     

    if ((timestamp % 604800) == 0):
        item = {
            's': 'BTC',
            't': timestamp,
            'h': price,
            'l': price,
            'o': price,
            'c': price,
        }

        table.put_item(Item = item)

        try:
            result = table.get_item(
                Key = {
                    's': 'BTC',
                    't': (timestamp - 604800)
                }
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            if 'Item' in result:
                volume_api = requests.get('https://min-api.cryptocompare.com/data/v2/histoday?fsym=BTC&tsym=USD&limit=7&api_key=52d6bec486eaf67f12a1462e29f2fa83b047b7ffb6c953de9e6bdc0b84ef98c8')
                data = volume_api.json()["Data"]["Data"]
                volume = 0
                for i in range(0, 7):
                    volume += data[i]["volumeto"]

                expressionAttributeValues = {
                    ':x': 0,
                    ':v': Decimal(str(volume))
                }
                if ((result['Item']['c'] - result['Item']['o']) != 0):
                    expressionAttributeValues.update({':x': round((((result['Item']['c'] - result['Item']['o']) / result['Item']['o']) * 100), 10)})

                update_result = table.update_item(
                    Key = {
                        's': 'BTC',
                        't': (timestamp - 604800)
                    },
                    UpdateExpression = "set x = :x, v = :v",
                    ExpressionAttributeValues = expressionAttributeValues,
                    ReturnValues="UPDATED_NEW"
                )

    else:
        try:
            result = table.get_item(
                Key = {
                    's': 'BTC',
                    't': (timestamp - (timestamp % 604800))
                }
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            if 'Item' in result:
                key = {
                    's': 'BTC',
                    't': (timestamp - (timestamp % 604800))
                }
                updateExpression = "set c = :c"
                expressionAttributeValues = {
                    ':c': price
                }

                if (result['Item']['h'] < price):
                    updateExpression = "set c = :c, h = :h"
                    expressionAttributeValues.update({':h': price})

                if (result['Item']['l'] > price):
                    updateExpression = "set c = :c, l = :l"
                    expressionAttributeValues.update({':l': price})

                if ((result['Item']['h'] < price) and (result['Item']['l'] > price)):
                    updateExpression = "set c = :c, h = :h, l = :l"

                update_result = table.update_item(
                    Key = key,
                    UpdateExpression = updateExpression,
                    ExpressionAttributeValues = expressionAttributeValues,
                    ReturnValues = "UPDATED_NEW"
                )

def month(timestamp, price):
    table = dynamodb.Table('BTC_month_free')     

    if ((timestamp % 2628000) == 0):
        item = {
            's': 'BTC',
            't': timestamp,
            'h': price,
            'l': price,
            'o': price,
            'c': price,
        }

        table.put_item(Item = item)

        try:
            result = table.get_item(
                Key = {
                    's': 'BTC',
                    't': (timestamp - 2628000)
                }
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            if 'Item' in result:
                volume_api = requests.get('https://min-api.cryptocompare.com/data/v2/histohour?fsym=BTC&tsym=USD&limit=730&api_key=52d6bec486eaf67f12a1462e29f2fa83b047b7ffb6c953de9e6bdc0b84ef98c8')
                data = volume_api.json()["Data"]["Data"]
                volume = 0
                for i in range(0, 730):
                    volume += data[i]["volumeto"]

                expressionAttributeValues = {
                    ':x': 0,
                    ':v': Decimal(str(volume))
                }
                if ((result['Item']['c'] - result['Item']['o']) != 0):
                    expressionAttributeValues.update({':x': round((((result['Item']['c'] - result['Item']['o']) / result['Item']['o']) * 100), 10)})

                update_result = table.update_item(
                    Key = {
                        's': 'BTC',
                        't': (timestamp - 2628000)
                    },
                    UpdateExpression = "set x = :x, v = :v",
                    ExpressionAttributeValues = expressionAttributeValues,
                    ReturnValues="UPDATED_NEW"
                )

    else:
        try:
            result = table.get_item(
                Key = {
                    's': 'BTC',
                    't': (timestamp - (timestamp % 2628000))
                }
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            if 'Item' in result:
                key = {
                    's': 'BTC',
                    't': (timestamp - (timestamp % 2628000))
                }
                updateExpression = "set c = :c"
                expressionAttributeValues = {
                    ':c': price
                }

                if (result['Item']['h'] < price):
                    updateExpression = "set c = :c, h = :h"
                    expressionAttributeValues.update({':h': price})

                if (result['Item']['l'] > price):
                    updateExpression = "set c = :c, l = :l"
                    expressionAttributeValues.update({':l': price})

                if ((result['Item']['h'] < price) and (result['Item']['l'] > price)):
                    updateExpression = "set c = :c, h = :h, l = :l"

                update_result = table.update_item(
                    Key = key,
                    UpdateExpression = updateExpression,
                    ExpressionAttributeValues = expressionAttributeValues,
                    ReturnValues = "UPDATED_NEW"
                )
