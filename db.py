# db.py
import mysql.connector
from mysql.connector import Error
from config import Config

def get_db_connection():
    try:
        return mysql.connector.connect(**Config.DB)
    except Error as e:
        print(f"[DB] Connection error: {e}")
        return None
