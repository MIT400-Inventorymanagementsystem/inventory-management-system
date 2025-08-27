from django.urls import path
from . import views
app_name = "sales"
urlpatterns = [
    path("customers/", views.CustomerList.as_view(), name="customer_list"),
    path("sales/",     views.SaleList.as_view(),     name="sale_list"),
    path("returns/",   views.ReturnList.as_view(),   name="return_list"),
    path("sales/new/",   views.SaleCreate.as_view(),   name="sale_new"),
    path("returns/new/", views.ReturnCreate.as_view(), name="return_new"),
]
