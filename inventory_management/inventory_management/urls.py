from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('products/', include('products.urls')),
    path('', lambda request: redirect('products:product_list')),  # Redirect root to products
]