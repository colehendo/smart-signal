DEPLOY:
 - To deploy everything, run:
    - sls deploy
 - To deploy one function, run:
    - sls deploy function -f `function name`


How to deal with Pandas and TA libraries:

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