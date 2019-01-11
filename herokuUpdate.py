# !/usr/bin/python3
# Update coins.db database daily from binance 24 hr changes.
# Author: cssanchez

from requests import get as curl
from datetime import datetime

import psycopg2 as postgre
from psycopg2.sql import SQL, Identifier
import os

"""
THIS FILE updates Heroku's PostGreSQL coins.db
"""

#### HEROKU CODE BELOW
DATABASE_URL = os.environ['DATABASE_URL']
coinsdb = postgre.connect(DATABASE_URL, sslmode='require')
sql_cursor = coinsdb.cursor()
utcnow = datetime.utcnow()  # datetime obj for used for runtime measurement

def debug():
    # Debugging to access database.
    # TODO: write SELECT DISTICT query for dates (without time),
    # TODOL update plotcoins to take hourly data into consideration.
    c = sql_cursor
    c.execute("SELECT * FROM quoteVolume;")
    qv = c.fetchall()
    c.execute("SELECT * FROM log;")
    logs = c.fetchall()
    print( f"Number of rows in quotevolume: {len(qv)}" )
    print( f"Latest Logs: {logs}" )
    return

# Hardcoded quotevolume as a random column. All tables should have same columns so shouldn't be a problem.
sql_cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = 'quotevolume';")
symbols = [ x[0] for x in sql_cursor.fetchall() ][1:] # Remove the timestamp column

sql_cursor.execute("SELECT tables FROM tables;")
tables = set( x[0] for x in sql_cursor.fetchall() ) - {'log', 'symbols', 'tables'}

def main():
    binanceURL = "https://api.binance.com//api/v1/ticker/24hr"  # Can add symbol=LTCBTC for single trade stats.
    binance = curl(binanceURL).json()  # list object containing one dict of new data for each symbol

    trading_coins = ['BTC','ETH','SDT','BNB','USD','PAX', 'XRP', 'SDC']
    ignored_features = ["symbol", 'closeTime', 'firstId', 'lastId', 'openTime']

    # Check for new tables. Remember there are a few we left out on purpose from our db
    new_tables = set( binance[0].keys()) - tables.union( set(ignored_features) )
    for table in new_tables:
        # add_new_tables(new_tables, coinsdb, sql_cursor)
        log(f"NEW TABLE {table} FOUND. WHAT DO I DO!!!!")

    # Verify coins in binance haven't changed, otherwise need make changes to db before updating.
    binance_symbols = set(entry['symbol'].lower() for entry in binance)
    current_symbols = set(symbols)
    # If there is a new coin from today's data: add it to our symbols.list file and our database as a column.
    new_coins = binance_symbols - current_symbols
    if new_coins:
        # Check for new endings (aka new trading coins) which might break our analysis scripts.
        for coin in new_coins:
            if coin[-3:] not in trading_coins:
                log(f"NEW trading coin {coin} found, need to update endings on plotcoin.py.")

        # Add new coins to our database.
        add_new_columns(new_coins)

    # Keep removed coins in symbols because they'll still be in the database as columns.
    #  This is mostly for our curiosity.
    removed_coins = current_symbols - binance_symbols
    for coin in removed_coins:
        # print(f'Coin {coin} has been removed from the Binance API.')
        log(f'Coin {coin} has been removed from the Binance API.')

    # Create dict of feature -> symbol -> value
    d = dict()
    # Each feature is a table.
    # labels refers to the column names in the sql_command,
    # values is the list sent to cursor.execute
    for table in tables:
        d[table] = {"labels": 'Timestamp', "values": [utcnow] }

    # Fill the dict with values
    for entry in binance:
        for table in tables:
            d[table]['labels'] += f", {entry['symbol']}"
            d[table]['values'].append( entry[table] )

    # Create SQL command string to insert values into each feature's table
    for table in d:
        sql_command = f"INSERT INTO {table} ({d[table]['labels']}) VALUES ({('%s,'*len(d[table]['values']))[:-1]});"
        sql_cursor.execute(sql_command, d[table]['values'])

    coinsdb.commit()
    # Close our database connection
    sql_cursor.close()
    coinsdb.close()
    return  # END MAIN

"""
log(message): adds a row to the log table with utcnow timestamp with any important message such as new coins, etc.
"""
def log(msg):
    print(msg)
    sql_cursor.execute(f"INSERT INTO log(timestamp, message) VALUES(%s,%s);", [utcnow, msg])
    return # END log

'''
Function to add new tables from an iterable new_tables. This function isn't called automatically, it's here to be used at author's discretion.
'''
def add_new_tables(new_tables):
    for table in new_tables:
        print(f'New table found! Adding {table} to the database.')
        sql_cursor.execute(f"INSERT INTO tables(tables) VALUES(%s);", [table])
        sql_command = f"CREATE TABLE {feature} (\nTimestamp TIMESTAMP PRIMARY KEY,\n"
        for symbol in symbols:
            sql_command += f"{symbol} DOUBLE PRECISION,\n"

        sql_command = sql_command[:-2] + ");"
        sql_cursor.execute(sql_command)
    coinsdb.commit()
    tables = tables.union( new_tables )
    return # END add_new_tables

"""
Function to add a new coin (column) to each table in tables.
"""
def add_new_columns(new_cols):
    for coin in new_cols:
        log(f'New coin found! Adding {coin} to the database.')
        for table in tables:
            sql_cursor.execute( f"ALTER TABLE {table} ADD COLUMN {coin} DOUBLE PRECISION;")

    coinsdb.commit()
    return  # END ADD_NEW_COLUMN

if __name__ == '__main__':
    main()
