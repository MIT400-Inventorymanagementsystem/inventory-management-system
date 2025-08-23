from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

class Product(models.Model):
    """Product model matching your original database structure"""
    
    # Fields matching your original products table
    product_name = models.CharField(
        max_length=255, 
        unique=True, 
        help_text="Unique product name"
    )
    category = models.CharField(
        max_length=100, 
        blank=True, 
        help_text="Product category"
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Product price in dollars"
    )
    stock_quantity = models.PositiveIntegerField(
        default=0,
        help_text="Current stock quantity"
    )
    min_threshold = models.PositiveIntegerField(
        default=10,
        help_text="Minimum stock threshold for alerts"
    )
    description = models.TextField(
        blank=True,
        help_text="Product description"
    )
    created_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['product_name']
        verbose_name = "Product"
        verbose_name_plural = "Products"
    
    def __str__(self):
        return self.product_name
    
    @property
    def stock_status(self):
        """Return stock status similar to your original alert system"""
        if self.stock_quantity <= 0:
            return 'OUT_OF_STOCK'
        elif self.stock_quantity <= self.min_threshold:
            return 'LOW_STOCK'
        else:
            return 'IN_STOCK'
    
    @property
    def stock_status_display(self):
        """Display text for stock status"""
        status_map = {
            'OUT_OF_STOCK': 'OUT OF STOCK',
            'LOW_STOCK': 'LOW STOCK', 
            'IN_STOCK': 'IN STOCK'
        }
        return status_map.get(self.stock_status, 'UNKNOWN')
    
    @property
    def stock_status_class(self):
        """CSS class for color coding like your original system"""
        status_map = {
            'OUT_OF_STOCK': 'table-danger',    # Red
            'LOW_STOCK': 'table-warning',      # Yellow
            'IN_STOCK': 'table-success'        # Green
        }
        return status_map.get(self.stock_status, '')
    
    @classmethod
    def get_low_stock_products(cls):
        """Get products that need restocking - like your check_low_stock method"""
        return cls.objects.filter(stock_quantity__lte=models.F('min_threshold'))
    
    @classmethod
    def get_alert_count(cls):
        """Get count of products needing attention"""
        return cls.get_low_stock_products().count()
