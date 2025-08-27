from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ("id", "product_name", "category", "price",
                     "stock_quantity", "min_threshold", "last_updated")
    search_fields = ("product_name", "category", "description")  # ← required for autocomplete
    list_filter   = ("category",)
    ordering      = ("product_name",)
