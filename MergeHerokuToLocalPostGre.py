#!/usr/bin/env python
# coding: utf-8

from datetime import datetime
from requests import get as curl
import ujson as json
import pandas as pd
import numpy as np
from functools import reduce
import os

#Database Imports
import psycopg2 as postgre
from psycopg2.sql import SQL, Identifier
from sqlalchemy import create_engine

herokuDB = postgre.connect('MY CREDENTIALS')
hcursor = herokuDB.cursor()

localDB = postgre.connect('MY CREDENTIALS')
lcursor = localDB.cursor()


# def add_new_tables(new_tables, db, sql_cursor):
#     for table in new_tables:
#         print(f'New table found! Adding {table} to the database.')
#         sql_cursor.execute(f"INSERT INTO tables(tables) VALUES(%s);", [table])
#         sql_command = f"CREATE TABLE {feature} (\nTimestamp TIMESTAMP PRIMARY KEY,\n"
#         for symbol in symbols:
#             sql_command += f"{symbol} DOUBLE PRECISION,\n"

#         sql_command = sql_command[:-2] + ");"
#         sql_cursor.execute(sql_command)
#     db.commit()
#     return # END add_new_tables


# QUERY ALL TABLE NAMES 
hcursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';")
htables = set( x[0] for x in hcursor.fetchall() )

lcursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';")
tables = set( x[0] for x in lcursor.fetchall() )

assert( tables == htables )

# Merge:
for table in tables:
    # Handle these separately. We may not use these tables anymore as they were replaced by schema queries.
    if table in ['symbols', 'tables']:
        continue
    
    # QUERY ALL COLUMN NAMES FOR THIS TABLE
    hcursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}';")
    hsymbols = [x[0] for x in hcursor.fetchall() ]
    
    lcursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}';")
    lsymbols = [x[0] for x in lcursor.fetchall() ]
    
    # If there are new coins, add them as columns before we add rows. 
    if hsymbols > lsymbols:
        new_cols = hsymbols[len(lsymbols):]
        for coin in new_cols:
            print(f'New coin found! Adding {coin} to {table}')
            lcursor.execute( f"ALTER TABLE {table} ADD COLUMN {coin} DOUBLE PRECISION;")
            # NOTE: Using psycopg2.SQL and Identifier to parse table and column names does not work properly 
            #   and sometimes gives random errors. We found it a random problem with the parser, since sqlite works fine.
        localDB.commit()
        
    # If Heroku has less columns than our local DB something weird happened.
    elif len(hsymbols) < len(lsymbols):
        print(f"ERROR heroku DB has less columns than our local one. \n HEROKU: {hsymbols} \n LOCAL: {lsymbols}")
    
    # Get latest local timestamp.
    lcursor.execute(f"SELECT timestamp FROM {table} ORDER BY timestamp DESC LIMIT 1;")
    latest_ts_local = lcursor.fetchall()[0][0]
    
    # Check for new rows in Heroku accoding to our last local timestamp.
    hcursor.execute(f"SELECT * FROM {table} WHERE timestamp > %s", [latest_ts_local])
    newRows = hcursor.fetchall()
    
    # Insert new rows into our localDB
    if newRows:
        for row in newRows:
            lcursor.execute(f"INSERT INTO {table} ({','.join(hsymbols)}) VALUES ({('%s,'*len(hsymbols))[:-1]})", row)

        print(f"INSERTED {len(newRows)} rows into {table} ending at {newRows[-1][0]}")

localDB.commit()
print(f"ALL DONE UPDATING LOCAL POSTGRE DB!")
print(f"Time finished (local time): {datetime.utcnow()}")

## PRINT LOG AFTER DONE UPDATING.
hcursor.execute(f"SELECT * FROM log;")
print( hcursor.fetchall() )
