"""
Inventory Management System – Reports & Analytics
Author: Punam
Module: Dashboard KPIs & Charts (Inventory, Sales, Returns)

This module computes high-level KPIs and chart series for the admin dashboard:
- Inventory status (in/low/out), current inventory value, category breakdown
- Customer & sales counts, revenue, returns, and return rate
- Sales aggregated by day (last 30 days)
- Top products by quantity and revenue
"""

from datetime import timedelta
from decimal import Decimal

from django.db.models import Sum, Count, F, DecimalField
from django.db.models.functions import TruncDate
from django.shortcuts import render
from django.utils import timezone

from products.models import Product
from sales.models import Customer, Sale, Return

def dashboard(request): # Build KPI cards and chart data for the dashboard page.
    # Inventory KPIs (Karuna)
    # Count of products at/below their minimum threshold (needs restock)
    low_stock_count = Product.objects.filter(stock_quantity__lte=F('min_threshold')).count()
    # Total inventory valuation = sum(stock_quantity * price) across products
    inventory_value = Product.objects.aggregate(
        total=Sum(F('stock_quantity') * F('price'),
                  output_field=DecimalField(max_digits=14, decimal_places=2))
    )['total'] or Decimal('0.00')

    # Status buckets for quick donut/pill cards:
    stock_counts = {
        'in':  Product.objects.filter(stock_quantity__gt=F('min_threshold')).count(),
        'low': Product.objects.filter(stock_quantity__gt=0,
                                      stock_quantity__lte=F('min_threshold')).count(),
        'out': Product.objects.filter(stock_quantity__lte=0).count(),
    }

    # Category breakdown (count of SKUs and total value per category)
    cats = (Product.objects.values('category')
            .annotate(n=Count('id'),
                      value=Sum(F('stock_quantity') * F('price'),
                                output_field=DecimalField(max_digits=14, decimal_places=2)))
            .order_by()) # keeps natural grouping without forcing an ORDER BY field
    category_labels = [c['category'] or 'Uncategorized' for c in cats]
    category_counts = [int(c['n'] or 0) for c in cats]
    category_values = [float(c['value'] or 0) for c in cats]

    # Sales/Returns KPIs (Sadhana)
    total_customers = Customer.objects.count()
    total_sales     = Sale.objects.count()
    total_revenue   = float(Sale.objects.aggregate(t=Sum('total_amount'))['t'] or 0)
    total_returns   = Return.objects.count()

    # Return rate (%) = returns / sales * 100
    return_rate     = round((total_returns / total_sales * 100), 2) if total_sales else 0.0

    today = timezone.now().date()
    start = today - timedelta(days=29) # generates 30 days including today

    # Aggregate revenue and quantity per day
    by_day = (Sale.objects.filter(sale_date__date__gte=start, sale_date__date__lte=today)
              .annotate(d=TruncDate('sale_date'))
              .values('d')
              .annotate(revenue=Sum('total_amount'), qty=Sum('quantity'))
              .order_by('d'))
    
    # Build a dense (no gaps) series for charts, filling missing days with zeros
    day_map = {row['d']: row for row in by_day}
    sales_day_labels, sales_rev_series, sales_qty_series = [], [], []
    for i in range(30):
        d = start + timedelta(days=i)
        sales_day_labels.append(d.strftime('%Y-%m-%d'))
        sales_rev_series.append(float((day_map.get(d) or {}).get('revenue') or 0))
        sales_qty_series.append(int((day_map.get(d) or {}).get('qty') or 0))

    # Top 5 products (qty)
    top = (Sale.objects.values('product__product_name')
           .annotate(total_qty=Sum('quantity'), revenue=Sum('total_amount'))
           .order_by('-total_qty')[:5])
    top_labels = [t['product__product_name'] for t in top]
    top_qty    = [int(t['total_qty'] or 0) for t in top]
    top_rev    = [float(t['revenue'] or 0) for t in top]

    # Render with context
    ctx = {
        # inventory KPIs
        "low_stock_count": low_stock_count,
        "inventory_value": float(inventory_value or 0),
        "stock_counts": stock_counts,
        "category_labels": category_labels,
        "category_counts": category_counts,
        "category_values": category_values,
        # sales/returns KPIs
        "total_customers": total_customers,
        "total_revenue": total_revenue,
        "total_sales": total_sales,
        "total_returns": total_returns,
        "return_rate": return_rate,
        # charts
        "sales_day_labels": sales_day_labels,
        "sales_rev_series": sales_rev_series,
        "sales_qty_series": sales_qty_series,
        "top_labels": top_labels,
        "top_qty": top_qty,
        "top_rev": top_rev,
    }
    return render(request, "reports/dashboard.html", ctx)
