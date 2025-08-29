import pandas as pd
import streamlit as st
from db import query_df
from dao import (
    create_sale, add_sale_item,
    get_top_sellers, get_revenue_by_day, get_low_stock,
    get_products, get_customers
)

st.set_page_config(page_title="Inventory Management", layout="wide")
st.title("Inventory Management Dashboard")

tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Create Sale", "Reports", "Low Stock"])

with tab1:
    st.subheader("Quick Stats")
    df_top = pd.DataFrame(get_top_sellers(5))
    df_rev = pd.DataFrame(get_revenue_by_day())
    df_low = pd.DataFrame(get_low_stock())

    c1, c2, c3 = st.columns(3)
    c1.metric("Products with Low Stock", len(df_low))
    c2.metric("Days Recorded", len(df_rev))
    c3.metric("Top Sellers Listed", len(df_top))

    st.write("### Top Sellers")
    st.dataframe(df_top, use_container_width=True)

with tab2:
    st.subheader("Create a Sale (stored procedures)")
    customers = get_customers()
    products = get_products()

    customer_map = {c["customer_name"]: c["customer_id"] for c in customers}
    product_map  = {p["product_name"]: (p["product_id"], p["quantity_in_stock"]) for p in products}

    sel_customer = st.selectbox("Customer", list(customer_map.keys()))
    if st.button("Start Sale"):
        sale_id = create_sale(customer_map[sel_customer], None)
        st.session_state["sale_id"] = sale_id
        st.success(f"Sale started. sale_id = {sale_id}")

    sale_id = st.session_state.get("sale_id")
    if sale_id:
        st.write(f"Active sale_id: **{sale_id}**")
        sel_product = st.selectbox("Product", list(product_map.keys()))
        qty = st.number_input("Quantity", min_value=1, value=1, step=1)

        if st.button("Add Item"):
            pid, _ = product_map[sel_product]
            try:
                add_sale_item(sale_id, pid, qty)
                st.success("Item added and stock updated.")
            except Exception as e:
                st.error(str(e))

        st.write("Current Sale Lines")
        df_lines = query_df(
            "SELECT sd.sale_detail_id, p.product_name, sd.quantity, sd.unit_price, sd.subtotal "
            "FROM sale_details sd JOIN products p ON p.product_id=sd.product_id "
            "WHERE sd.sale_id=%s", (sale_id,)
        )
        st.dataframe(df_lines, use_container_width=True)

        df_sale = query_df("SELECT * FROM sales WHERE sale_id=%s", (sale_id,))
        if not df_sale.empty:
            st.info(f"Total: ${df_sale.iloc[0]['total_amount']:.2f}")

with tab3:
    st.subheader("Revenue by Day")
    df = pd.DataFrame(get_revenue_by_day())
    st.dataframe(df, use_container_width=True)
    if not df.empty:
        st.line_chart(df.set_index("sale_day")["revenue"])

    st.subheader("Top Sellers")
    df = pd.DataFrame(get_top_sellers(10))
    st.dataframe(df, use_container_width=True)
    if not df.empty:
        st.bar_chart(df.set_index("product_name")["total_qty_sold"])

with tab4:
    st.subheader("Low Stock Alerts")
    df = pd.DataFrame(get_low_stock())
    st.dataframe(df, use_container_width=True)