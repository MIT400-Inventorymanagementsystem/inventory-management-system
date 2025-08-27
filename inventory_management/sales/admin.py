# Module: Customer, Sales & Returns Admin Interface
from django.contrib import admin
from .models import Customer, Sale, Return

# Customer Admin
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display    = ("first_name", "last_name", "email", "phone", "registration_date")
    search_fields   = ("first_name", "last_name", "email", "phone")
    ordering        = ("first_name", "last_name")
    date_hierarchy  = "registration_date"

# Inline: Return inside Sale
class ReturnInline(admin.TabularInline):
    model = Return
    extra = 0
    autocomplete_fields = ("product",)
    fields = ("product", "quantity", "return_reason", "return_date")

# Sale Admin
@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display        = ("id", "customer", "product", "quantity",
                           "unit_price", "total_amount", "sale_date")
    list_filter         = ("sale_date",)
    search_fields       = ("customer__first_name", "customer__last_name",
                           "product__product_name")
    autocomplete_fields = ("customer", "product")
    readonly_fields     = ("total_amount",)
    list_select_related = ("customer", "product")
    date_hierarchy      = "sale_date"
    inlines             = [ReturnInline]

# Return Admin
@admin.register(Return)
class ReturnAdmin(admin.ModelAdmin):
    list_display        = ("id", "sale", "product", "quantity", "return_reason", "return_date")
    list_filter         = ("return_date",)
    autocomplete_fields = ("sale", "product")
    list_select_related = ("sale", "product")
    date_hierarchy      = "return_date"


