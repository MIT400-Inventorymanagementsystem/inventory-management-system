from db import get_conn

def create_sale(customer_id: int, sale_date: str | None = None) -> int:
    with get_conn() as cn, cn.cursor() as cur:
        cur.callproc("sp_create_sale", (customer_id, sale_date, 0))
        cur.execute("SELECT MAX(sale_id) FROM sales")
        (sale_id,) = cur.fetchone()
        return int(sale_id)

def add_sale_item(sale_id: int, product_id: int, qty: int):
    with get_conn() as cn, cn.cursor() as cur:
        cur.callproc("sp_add_sale_item", (sale_id, product_id, qty))
        cn.commit()

def get_top_sellers(limit: int = 10):
    with get_conn() as cn, cn.cursor(dictionary=True) as cur:
        cur.execute("SELECT * FROM v_top_sellers LIMIT %s", (limit,))
        return cur.fetchall()

def get_revenue_by_day():
    with get_conn() as cn, cn.cursor(dictionary=True) as cur:
        cur.execute("SELECT * FROM v_revenue_by_day")
        return cur.fetchall()

def get_low_stock():
    with get_conn() as cn, cn.cursor(dictionary=True) as cur:
        cur.execute("SELECT * FROM v_low_stock")
        return cur.fetchall()

def get_products():
    with get_conn() as cn, cn.cursor(dictionary=True) as cur:
        cur.execute("SELECT product_id, product_name, quantity_in_stock, reorder_level FROM products")
        return cur.fetchall()

def get_customers():
    with get_conn() as cn, cn.cursor(dictionary=True) as cur:
        cur.execute("SELECT customer_id, customer_name FROM customers ORDER BY customer_name")
        return cur.fetchall()