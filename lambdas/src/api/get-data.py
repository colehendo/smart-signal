import time
import simplejson as json

import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")


def get_data(event, context):
    print(event)
    if event["queryStringParameters"] == None:
        return {
            "statusCode": 502,
            "body": json.dumps("No parameters given"),
            "headers": {"Access-Control-Allow-Origin": "*"},
        }
    if event["queryStringParameters"]["timeframes"] == None:
        return {
            "statusCode": 502,
            "body": json.dumps("No data given"),
            "headers": {"Access-Control-Allow-Origin": "*"},
        }

    # Load the payload into a usable format
    timeframes = json.loads(event["queryStringParameters"]["timeframes"])
    data = []
    largest_tf_found = False
    timestamp = int(time.time())

    month_ttl = 0
    month_gap = 2628000
    month_datapoints = 0

    week_ttl = 0
    week_gap = 604800
    week_datapoints = 0

    day_ttl = 157680000
    day_gap = 86400
    day_datapoints = 1825

    four_hour_ttl = 15768000
    four_hour_gap = 14400
    four_hour_datapoints = 1095

    hour_ttl = 2628000
    hour_gap = 3600
    hour_datapoints = 730

    fifteen_minute_ttl = 604800
    fifteen_minute_gap = 900
    fifteen_minute_datapoints = 672

    minute_ttl = 86400
    minute_gap = 60
    minute_datapoints = 1440

    if ("month" in timeframes) or (largest_tf_found):
        data.append(
            {
                "timeframe": "month",
                "tf_data": call_dynamo(
                    "BTC",
                    "BTC_month",
                    timestamp,
                    month_ttl,
                    month_gap,
                    month_datapoints,
                ),
            }
        )
        largest_tf_found = True
    if ("week" in timeframes) or (largest_tf_found):
        data.append(
            {
                "timeframe": "week",
                "tf_data": call_dynamo(
                    "BTC", "BTC_week", timestamp, week_ttl, week_gap, week_datapoints
                ),
            }
        )
        largest_tf_found = True
    if ("day" in timeframes) or (largest_tf_found):
        data.append(
            {
                "timeframe": "day",
                "tf_data": call_dynamo(
                    "BTC", "BTC_day", timestamp, day_ttl, day_gap, day_datapoints
                ),
            }
        )
        largest_tf_found = True
    if ("four_hour" in timeframes) or (largest_tf_found):
        data.append(
            {
                "timeframe": "four_hour",
                "tf_data": call_dynamo(
                    "BTC",
                    "BTC_four_hour",
                    timestamp,
                    four_hour_ttl,
                    four_hour_gap,
                    four_hour_datapoints,
                ),
            }
        )
        largest_tf_found = True
    if ("hour" in timeframes) or (largest_tf_found):
        data.append(
            {
                "timeframe": "hour",
                "tf_data": call_dynamo(
                    "BTC", "BTC_hour", timestamp, hour_ttl, hour_gap, hour_datapoints
                ),
            }
        )
        largest_tf_found = True
    if ("fifteen_minute" in timeframes) or (largest_tf_found):
        data.append(
            {
                "timeframe": "fifteen_minute",
                "tf_data": call_dynamo(
                    "BTC",
                    "BTC_fifteen_minute",
                    timestamp,
                    fifteen_minute_ttl,
                    fifteen_minute_gap,
                    fifteen_minute_datapoints,
                ),
            }
        )
        largest_tf_found = True
    if ("minute" in timeframes) or (largest_tf_found):
        data.append(
            {
                "timeframe": "minute",
                "tf_data": call_dynamo(
                    "BTC",
                    "BTC_minute",
                    timestamp,
                    minute_ttl,
                    minute_gap,
                    minute_datapoints,
                ),
            }
        )
        largest_tf_found = True

    print(data)

    return {
        "statusCode": 200,
        "body": json.dumps(data),
        "headers": {"Access-Control-Allow-Origin": "*"},
    }

    # Extract the relevant data and order chronologically
    # prices = [{"h": x["h"], "l": x["l"], "o": x["o"], "c": x["c"]}
    #         for x in items]

    # print(prices)

    # # Send them to the client who asked for it
    # data = {"prices": prices}


def call_dynamo(symbol, table, timestamp, ttl, gap, datapoints):
    table = dynamodb.Table(table)
    try:
        # Scan the table for all datapoints
        if datapoints > 0:
            results = table.query(
                KeyConditionExpression=Key("s").eq(symbol)
                & Key("t").gt((timestamp + ttl) - (gap * datapoints))
            )
        else:
            results = table.scan()
    except ClientError as e:
        print(e.response["Error"]["Code"])
        print(e.response["ResponseMetadata"]["HTTPStatusCode"])
        print(e.response["Error"]["Message"])
    else:
        if "Items" in results:
            # Turn the returned object into a JSON string,
            # and pass it to pandas to make it readable for TA
            for i in range(0, len(results["Items"])):
                results["Items"][i]["t"] = results["Items"][i]["t"] - ttl
            return results["Items"]
        else:
            return []