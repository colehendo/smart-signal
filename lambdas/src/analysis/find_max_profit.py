import simplejson as json
import numpy as np
import pandas as pd
import boto3
from botocore.exceptions import ClientError
from scipy.signal import argrelextrema

dynamodb = boto3.resource("dynamodb")
paginator = dynamodb.meta.client.get_paginator("scan")


def find_max_profit(event, context):
    if event["queryStringParameters"] == None:
        return {
            "statusCode": 502,
            "body": json.dumps("No parameters given"),
            "headers": {"Access-Control-Allow-Origin": "*"},
        }

    # The length of time before closing a position
    time_gap = int(event["queryStringParameters"]["time_gap"])

    if not time_gap:
        return {
            "statusCode": 502,
            "body": json.dumps("No time gap given"),
            "headers": {"Access-Control-Allow-Origin": "*"},
        }

    prices = []

    try:
        # Scan the table for all price data
        pages = paginator.paginate(TableName="BTC_day_static")
    except Exception as _e:
        print("Exception with price table:")
        print(str(_e))
        raise
    else:
        for page in pages:
            for price in page["Items"]:
                prices.append(price)

    df = pd.DataFrame(prices)

    all_min = df.iloc[
        argrelextrema(df.c.values, np.greater_equal, order=int(time_gap / 2))[0]
    ][["t"]]
    all_min["sig"] = "sell"
    all_max = df.iloc[
        argrelextrema(df.c.values, np.less_equal, order=int(time_gap / 2))[0]
    ][["t"]]
    all_max["sig"] = "buy"

    extremes = pd.concat([all_min, all_max])
    extremes.sort_values(by="t", inplace=True)

    return extremes
