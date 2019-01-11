# !/usr/bin/python3
# Update coins.db database daily from binance 24 hr changes.
# Author: Carlos Sanchez


"""
THIS Script initializes an empty Heroku DB hooked to this Dyno with the current Binance symbols/tables.
"""

from requests import get as curl
import json
from datetime import datetime

import psycopg2 as postgre
import os


with open('symbols.list','r') as f:
    symbols = json.load(f)

with open('tables.list','r') as f:
    tables = json.load(f)

"""
This function is called when database is empty. So we need to init everything from tables to columns.
"""
def main():
    utcnow = datetime.utcnow()  # datetime obj for used for runtime measurement

    binanceURL = "https://api.binance.com//api/v1/ticker/24hr"  # Can add symbol=LTCBTC for single trade stats.
    binance = curl(binanceURL).json()  # list object containing one dict of new data for each symbol

    #### HEROKU CODE BELOW
    DATABASE_URL = os.environ['DATABASE_URL']
    coinsdb = postgre.connect(DATABASE_URL, sslmode='require')
    sql_cursor = coinsdb.cursor()

    d = dict()
    for feature in tables:
        d[feature] = dict()

    # Fill the dict with values
    for entry in binance:
        for feature in tables:
            d[feature][entry['symbol']] = entry[feature]

    for feature in d:
        sql_command = f"CREATE TABLE {feature} (\nTimestamp TIMESTAMP PRIMARY KEY,\n"
        for symbol in d[feature]:
            sql_command += f"{symbol} DOUBLE PRECISION,\n"

        sql_command = sql_command[:-2] + ");"
        sql_cursor.execute(sql_command)

    sql_cursor.execute(f"CREATE TABLE log (Timestamp TIMESTAMP, message TEXT);")
    sql_cursor.execute(f"CREATE TABLE symbols (symbols TEXT PRIMARY KEY);")
    sql_cursor.execute(f"CREATE TABLE tables (tables TEXT PRIMARY KEY);")

    coinsdb.commit()

    # Now populate symbols and tables.
    for table in tables:
        sql_cursor.execute(f"INSERT INTO tables(tables) VALUES (%s);", [table])

    for symbol in symbols:
        sql_cursor.execute(f"INSERT INTO symbols(symbols) VALUES (%s);", [symbol])

    coinsdb.commit()

    # Close our database connection
    sql_cursor.close()
    coinsdb.close()
    return # END initPostgre

if __name__ == '__main__':
    main()
