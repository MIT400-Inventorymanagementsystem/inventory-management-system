from dao import get_top_sellers, get_revenue_by_day, create_sale, add_sale_item

def test_views_not_empty():
    assert len(get_revenue_by_day()) >= 1
    assert len(get_top_sellers(5)) >= 1

def test_transaction_flow():
    sale_id = create_sale(1, None)
    assert isinstance(sale_id, int) and sale_id > 0
    add_sale_item(sale_id, 1, 1)