
import sqlite3
import psycopg2
import sqlalchemy


def connect(host='localhost', user=None, password=None, port=None):
    # stuff

def add_columns(columns_names, columns_types):
    assert(len(columns_names) == len(columns_types))

    for x in range(len(columns_names)):
        self.cursor.execute()