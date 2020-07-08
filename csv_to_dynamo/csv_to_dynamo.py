import csv
import boto3
import os
from decimal import Decimal
import time

os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

def convert_csv_to_json_list(file):
   items = []
   with open(file) as csvfile:
      reader = csv.DictReader(csvfile)
      for row in reader:
      	# int(row['time'])<1597838400 and int(row['time'])>1566292400)
      	  if(int(row['time'])>1579461200):
	          data = {}
	          # data['Date'] = row['ï»¿Date']
	          # data['Price'] = Decimal(row['Price'])
	          data['o'] = Decimal(row['open'])
	          data['h'] = Decimal(row['high'])
	          data['l'] = Decimal(row['low'])
	          data['c']= Decimal(row['close'])
	          # data['Vol.'] = row['Vol.'] 
	          if row['Volume'][-1] == 'k':
	          	row['Volume'] = row['Volume'][:-1]
	          	data['v']= Decimal(row['Volume'])*1000
	          elif row['Volume'][-1] == 'M':
	          	row['Volume'] = row['Volume'][:-1]
	          	data['v'] = Decimal(row['Volume'])*1000000
	          else:
	          	data['v'] = Decimal(row['Volume'])
	          # data['Change%'] = row['Change %']
	          data['s'] = 'BTC'
	          data['t'] = int(row['time'])+2628000
	          data['x'] = round(((Decimal(row['close'])- Decimal(row['open']))/Decimal(row['open'])) * 100, 10)
	          # populate remaining fields here
	          #................
	          items.append(data)
   return items

def batch_write(items):
   dynamodb = boto3.resource('dynamodb')
   db = dynamodb.Table('BTC_hour')

   # with db.batch_writer() as batch:
   for item in items:
    db.put_item(Item=item)
    time.sleep(.5)



if __name__ == '__main__':
   json_data = convert_csv_to_json_list('GEMINI_BTCUSD, 60.csv')
   batch_write(json_data)

