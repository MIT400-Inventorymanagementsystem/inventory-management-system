import os
from dotenv import load_dotenv
import mysql.connector as mysql

load_dotenv()

conn = mysql.connect(
    host=os.getenv("DB_HOST", "127.0.0.1"),
    port=int(os.getenv("DB_PORT", "3306")),
    user=os.getenv("DB_USER", "app_viewer"),
    password=os.getenv("DB_PASS", ""),
    database=os.getenv("DB_NAME", "inventory_mgmt"),
)
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM products;")
count = cur.fetchone()[0]
print("OK! Connected. products rows:", count)

cur.close()
conn.close()
