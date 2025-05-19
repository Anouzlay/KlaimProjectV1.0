# patch_sqlite.py
import sys
import sqlite3
import pysqlite3
import os

def patch_sqlite():
    print("Current SQLite version:", sqlite3.sqlite_version)
    
    try:
    
        sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
        print("SQLite patched with pysqlite3")
        print("New SQLite version:", sqlite3.sqlite_version)
    except ImportError:
        print("pysqlite3 not found, using system SQLite")
