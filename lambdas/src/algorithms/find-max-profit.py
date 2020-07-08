import simplejson as json

import boto3
from botocore.exceptions import ClientError
dynamodb = boto3.resource('dynamodb')
paginator = dynamodb.meta.client.get_paginator('scan')

def find_max_profit(event, context):
    if (event['queryStringParameters'] == None):
        return {
            "statusCode": 502,
            "body": json.dumps("No parameters given"),
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }

    # The length of time before closing a position
    time_gap = int(event['queryStringParameters']['time_gap'])

    if not time_gap:
        return {
            "statusCode": 502,
            "body": json.dumps("No time gap given"),
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }

    prices = []

    try:
        # Scan the table for all price data
        pages = paginator.paginate(TableName='BTC_day_static')
    except Exception as _e:
        print('Exception with price table:')
        print(str(_e))
        raise
    else:
        for page in pages:
            for price in page['Items']:
                prices.append(price)

    for price in prices:
        print('filler to rid errors')
        # run array of prices front to back
        # keep track of the lowest recorded price, highest recorded price

        # if the price starts rising a significant amount, mark that low as the buy point
        # if the price starts dipping a significant amount, mark that high as the sell point
        # the significant amount should be a relational value based on the time_gap variable (TODO FOR PATRICK)

        # if you are looking for a sell and (previous_buy_timestamp < (current_price_timestamp - time_gap)) then mark current max as sell
        # record profit from respective buys and sells
        # profit should be recorded through metric like ROI, although a more accurate one, or set of metrics, probably exist

    # run through prices again most recent to most historical, using the same strategy as above, but backwards for buys & sells
    # compare back to front profit to front to back

    # do another set of loops, seeing if buying between recorded positions and selling between the next recorded positions is more profitable
    # continue these loops until a maximum profit is found
