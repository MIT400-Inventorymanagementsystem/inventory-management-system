from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from .models import Customer, Sale, Return
from .forms import CustomerForm, SaleForm, ReturnForm

# List Views
class CustomerList(ListView):
    """
    Displays a list of all customers.
    Template: sales/customers.html
    Context: 'customers'
    """
    model = Customer
    template_name = "sales/customers.html"
    context_object_name = "customers"

class SaleList(ListView):
    """
    Displays a list of all sales.
    Template: sales/sales.html
    Context: 'sales'
    """
    model = Sale
    template_name = "sales/sales.html"
    context_object_name = "sales"

class ReturnList(ListView):
    """
    Displays a list of all returns.
    Template: sales/returns.html
    Context: 'returns'
    """
    model = Return
    template_name = "sales/returns.html"
    context_object_name = "returns"

# Create Views
class SaleCreate(CreateView):
    """
    Create a new Sale.
    - On success: redirects to sales list, shows success message
    - On failure (e.g., insufficient stock): adds error to form, stays on page
    """
    model = Sale
    form_class = SaleForm
    template_name = "sales/form.html"
    success_url = reverse_lazy("sales:sale_list")
    def form_valid(self, form):
        try:
            messages.success(self.request, "Sale recorded.") # success feedback
            return super().form_valid(form)
        except Exception as e:
            # If save() raised ValueError or ValidationError, show in form
            form.add_error(None, str(e))
            return super().form_invalid(form)

class ReturnCreate(CreateView):
    """
    Create a new Return.
    - Validates return logic (via model.clean)
    - On success: redirects to return list with success message
    - On failure: error messages appear on form
    """
    model = Return
    form_class = ReturnForm
    template_name = "sales/form.html"
    success_url = reverse_lazy("sales:return_list")
