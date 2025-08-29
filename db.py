import os
import mysql.connector
from mysql.connector import pooling
from dotenv import load_dotenv

load_dotenv()

config = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASS", "@@Himal@@"),
    "database": os.getenv("DB_NAME", "inventory_mgmt"),
    "auth_plugin": "mysql_native_password",
}

pool = pooling.MySQLConnectionPool(pool_name="inv_pool", pool_size=5, **config)

def get_conn():
    return pool.get_connection()

def query_df(sql: str, params: tuple = ()):
    import pandas as pd
    with get_conn() as cn, cn.cursor(dictionary=True) as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
    return pd.DataFrame(rows)

def execute(sql: str, params: tuple = ()):
    with get_conn() as cn, cn.cursor() as cur:
        cur.execute(sql, params)
        cn.commit()
        return cur.rowcount