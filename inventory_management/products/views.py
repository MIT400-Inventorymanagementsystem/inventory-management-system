from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, F
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Product
from .forms import ProductForm, ProductSearchForm

class ProductListView(ListView):
    """Main product list view - replaces your main tkinter window"""
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 20
    
    def get_queryset(self):
        """Handle search functionality - like your search_products method"""
        queryset = Product.objects.all()
        
        # Get search parameters
        search_query = self.request.GET.get('search_query', '').strip()
        category = self.request.GET.get('category', '').strip()
        show_low_stock = self.request.GET.get('show_low_stock')
        
        # Apply search filters
        if search_query:
            queryset = queryset.filter(
                Q(product_name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        if category:
            queryset = queryset.filter(category__icontains=category)
        
        # Show only low stock items - like your show_low_stock_items method
        if show_low_stock:
            queryset = queryset.filter(stock_quantity__lte=F('min_threshold'))
        
        return queryset.order_by('product_name')
    
    def get_context_data(self, **kwargs):
        """Add extra context - like your alert system"""
        context = super().get_context_data(**kwargs)
        
        # Add search form
        context['search_form'] = ProductSearchForm(self.request.GET)
        
        # Add alert information - like your update_alert_display method
        context['alert_count'] = Product.get_alert_count()
        context['low_stock_products'] = Product.get_low_stock_products()
        
        # Add current search parameters
        context['current_search'] = self.request.GET.get('search_query', '')
        context['current_category'] = self.request.GET.get('category', '')
        context['showing_low_stock'] = bool(self.request.GET.get('show_low_stock'))
        
        return context


class ProductCreateView(CreateView):
    """Create product view - replaces your add_product_dialog"""
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('products:product_list')
    
    def form_valid(self, form):
        """Handle successful form submission - like your add_product method"""
        messages.success(self.request, f'Product "{form.instance.product_name}" added successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Handle form errors - like your validation error handling"""
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class ProductUpdateView(UpdateView):
    """Update product view - replaces your update_product_dialog"""
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('products:product_list')
    
    def form_valid(self, form):
        """Handle successful update - like your update_product method"""
        messages.success(self.request, f'Product "{form.instance.product_name}" updated successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Handle form errors"""
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class ProductDeleteView(DeleteView):
    """Delete product view - replaces your delete_product_dialog"""
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('products:product_list')
    
    def delete(self, request, *args, **kwargs):
        """Handle successful deletion - like your delete_product method"""
        product_name = self.get_object().product_name
        messages.success(request, f'Product "{product_name}" deleted successfully!')
        return super().delete(request, *args, **kwargs)


def ajax_search_products(request):
    """AJAX search for real-time filtering"""
    if request.method == 'GET':
        search_query = request.GET.get('q', '').strip()
        
        if search_query:
            products = Product.objects.filter(
                Q(product_name__icontains=search_query) |
                Q(category__icontains=search_query)
            )[:10]  # Limit to 10 results
            
            results = [
                {
                    'id': product.id,
                    'name': product.product_name,
                    'category': product.category,
                    'stock_status': product.stock_status_display
                }
                for product in products
            ]
            
            return JsonResponse({'results': results})
        
        return JsonResponse({'results': []})