# !/usr/bin/python3
# Update coins.db database daily from binance 24 hr changes.
# Author: cssanchez

from requests import get as curl
import json
from datetime import datetime
import pandas as pd
import sqlite3


# TODO: make a report-style output for trending coins using historical data (make database for frequency I suppose)
# TODO identify pump n dump. (find spread between last 2 weeks)
# TODO: Fixed the Insertion query to use %s on execute.
# Read list of existing symbols from file.
#   List is useful for git-friendly, human-readable file. Sets are not json-serializable otherwise would use.
with open('symbols.list','r') as f:
    symbols = json.load(f)

with open('tables.list','r') as f:
    tables = json.load(f)

def main():
    utcnow = datetime.utcnow()  # datetime obj for used for runtime measurement
    time = str(utcnow)[11:-7]  # HH:MM:SS
    today = str(utcnow)[:10]  # YYYY-MM-DD

    binanceURL = "https://api.binance.com//api/v1/ticker/24hr"  # Can add symbol=LTCBTC for single trade stats.
    binance = curl(binanceURL).json()  # list object containing one dict of new data for each symbol
    coinsdb, sql_cursor = initSQL("coins.db")

    # Check for new tables. Remember there are a few we left out on purpose from our db
    new_tables = set(binance[0].keys()) - set(tables + ["symbol", 'closeTime', 'firstId', 'lastId', 'openTime'])
    if new_tables:
        add_new_tables(new_tables, coinsdb, sql_cursor)
    # Verify coins in binance haven't changed, otherwise need make changes to db before updating.
    binance_symbols = set(entry['symbol'] for entry in binance)
    current_symbols = set(symbols)
    # If there is a new coin from today's data: add it to our symbols.list file and our database as a column.
    new_coins = binance_symbols - current_symbols
    if new_coins:
        # Check for new endings (aka new trading coins) which might break our analysis scripts.
        for coin in new_coins:
            if coin[-3:] not in ['BTC','ETH','SDT','BNB','USD','PAX']:
                print(f"NEW ending {coin} found, need to update endings on plotcoin.py. ASAP !!!! \n URGENT Update needed for plotcoins.py")

        # Store newfound coins in our list of existing coins:
        with open("symbols.list",'w') as f:
            json.dump(symbols + list(new_coins), f)

        # Add new coins to our database.
        add_new_columns(new_coins, coinsdb, sql_cursor)

    # Keep removed coins in symbols because they'll still be in the database as columns.
    #  This is mostly for our curiosity.
    removed_coins = current_symbols - binance_symbols
    for coin in removed_coins:
        print(f'Coin {coin} has been removed from Binance.')


    # Create dict of feature -> symbol -> value
    d = dict()
    # Date feature is: STRING yyyy-mm-dd
    # Time feature is: STRING hh:mm:ss
    for feature in tables:
        d[feature] = dict(Date=today, Time=time)
    # Fill the dict with values
    for entry in binance:
        for feature in tables:
            d[feature][entry['symbol']] = entry[feature]
    # Create SQL command string to insert values into each feature's table
    for feature in d:
        sql_command = "INSERT INTO " + feature + " ("
        values = "VALUES ("
        for column in d[feature]:
            sql_command += column + ", "
            if column in ["Date", "Time"]:  # Need to escape characters for the Time and Date strings for SQL to process
                values += "\"" + str(d[feature][column]) + "\", "
            else:
                values += str(d[feature][column]) + ", "
        sql_command = sql_command[:-2] + ") " + values[:-2] + ");"
        sql_cursor.execute(sql_command)
        coinsdb.commit()
    print(f"Done updating coins.db took: {datetime.utcnow() - utcnow}")
    return  # END MAIN

def initSQL(dbName):
    db = sqlite3.connect(dbName)
    sql_cursor = db.cursor()
    return db, sql_cursor

def add_new_tables(new_tables, coinsdb, sql_cursor):
    for table in new_tables:
        print(f'New table found! Adding {table} to the database.')
        sql_command = "CREATE TABLE " + table + " (\n"
        sql_command += "Date CHAR(10) PRIMARY KEY,\n"
        sql_command += "Time CHAR(8),\n"
        for symbol in symbols:
            if symbol not in ['Date', 'Time']:
                sql_command += symbol + " REAL,\n"
        sql_command = sql_command[:-2] + ");"
        sql_cursor.execute(sql_command)
    coinsdb.commit()
    return


def add_new_columns(new_cols, coinsdb, sql_cursor):
    for coin in new_cols:
        print(f'New coin found! Adding {coin} to the database.')
        for table in tables:
            sql_command = "ALTER TABLE " + table + " ADD COLUMN " + coin + " REAL;"
            # RENAME COLUMN
            # sql_command = "ALTER TABLE " + table + " RENAME COLUMN " + "PAXUSDTREAL" + "TO" + "PAXUSDT;"
            sql_cursor.execute(sql_command)
    coinsdb.commit()
    return  # END ADD_NEW_COLUMN


if __name__ == '__main__':
    main()
