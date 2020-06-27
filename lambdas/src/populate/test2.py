import json
import time
import datetime
from decimal import Decimal
import requests


def main():
    # table = dynamodb.Table('BTC_second')
    # Increases the count by 1, breaks when index == 60
    # index = event['iterator']['index'] + 1
    i = 0
    print(time.time())

    while i < 1:
        # If it is at the start of a second period, run everything
        if ((time.time() % 1) < 0.1):
            timestamp = int(time.time())
            price = 10

            item = {
                's': 'BTC',
                't': (timestamp + 600),
                'p': price
            }

            # Write the new price value into the seconds table

            i += 1


if __name__ == "__main__":
    main()