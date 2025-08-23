from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Main product list - your main interface
    path('', views.ProductListView.as_view(), name='product_list'),
    
    # CRUD operations - replacing your tkinter dialogs
    path('add/', views.ProductCreateView.as_view(), name='product_add'),
    path('<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_edit'),
    path('<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    
    # AJAX search
    path('ajax/search/', views.ajax_search_products, name='ajax_search'),
    
    # Low stock filter
    path('low-stock/', views.ProductListView.as_view(), {'show_low_stock': True}, name='low_stock_products'),
]