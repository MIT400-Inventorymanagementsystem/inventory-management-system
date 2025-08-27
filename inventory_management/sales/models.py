from decimal import Decimal
from django.db import models, transaction
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from products.models import Product

# Customer Model
class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name  = models.CharField(max_length=100)
    email      = models.EmailField(unique=True, blank=True, null=True)
    phone      = models.CharField(max_length=30, blank=True)
    address    = models.TextField(blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["first_name", "last_name"] # Sort alphabetically by default

    def __str__(self):
        # Shows "First Last" in admin & dropdowns
        return f"{self.first_name} {self.last_name}".strip()

# Sale Model
class Sale(models.Model):
    customer    = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="sales")
    product     = models.ForeignKey(Product,  on_delete=models.PROTECT, related_name="sales")
    quantity    = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price  = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    total_amount= models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    sale_date   = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-sale_date"] # Most recent first

    def save(self, *args, **kwargs):
        """
        Override save() to:
        - Compute total_amount (quantity × unit_price)
        - Adjust product stock safely (atomic transactions)
        - Handle both create and update scenarios (delta-based stock adjustment)
        """
        with transaction.atomic():
            # lock row to avoid race updates in concurrent requests
            p = Product.objects.select_for_update().get(pk=self.product_id)

            # default unit_price to current product price if not provided
            if self.unit_price in (None, ""):
                self.unit_price = p.price

            # compute total
            self.unit_price = Decimal(self.unit_price)
            self.total_amount = self.unit_price * Decimal(self.quantity)

            # handle create vs update (adjust by delta)
            if self.pk:
                prev = Sale.objects.select_for_update().get(pk=self.pk)
                delta = self.quantity - prev.quantity
            else:
                delta = self.quantity

            # check stock for positive delta
            if delta > 0 and p.stock_quantity < delta:
                raise ValueError("Insufficient stock for this sale.")

            # apply stock change (decrement by delta; negative delta restores stock)
            if delta != 0:
                p.stock_quantity = p.stock_quantity - delta
                p.save(update_fields=["stock_quantity"])

            super().save(*args, **kwargs)

    def __str__(self):
        return f"Sale #{self.pk or 'new'} - {self.product} x {self.quantity}"            

# Return Model
class Return(models.Model):
    sale        = models.ForeignKey(Sale, on_delete=models.PROTECT, related_name="returns")
    product     = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="returns")
    quantity    = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    return_reason = models.CharField(max_length=255, blank=True)
    return_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-return_date"]

    def clean(self):
        """
        Validation before saving:
        - Ensure product matches the one in the original sale
        - Prevent cumulative returns > sale.quantity
        """
        if self.product_id and self.sale_id and self.product_id != self.sale.product_id:
            raise ValidationError("Return product must match the original sale product.")

        # Total already returned for this sale (excluding current record if updating)
        returned = self.sale.returns.exclude(pk=self.pk).aggregate(
            total=models.Sum("quantity")
        )["total"] or 0

        # New + old returns cannot exceed quantity sold
        if self.quantity + returned > self.sale.quantity:
            raise ValidationError("Return quantity exceeds quantity sold.")

    def save(self, *args, **kwargs):
        """
        Override save() to:
        - Run validation (clean)
        - Restore stock based on delta change
        """
        self.clean()  # run validations
        with transaction.atomic():
            p = Product.objects.select_for_update().get(pk=self.product_id)
            # Handle stock adjustment by delta (update vs create)
            if self.pk:
                prev = Return.objects.select_for_update().get(pk=self.pk)
                delta = self.quantity - prev.quantity
            else:
                delta = self.quantity
            
            # Apply stock restoration
            if delta != 0:
                p.stock_quantity = p.stock_quantity + delta
                p.save(update_fields=["stock_quantity"])
            
            # Save return record
            super().save(*args, **kwargs)

    def __str__(self):
        return f"Return #{self.pk or 'new'} - {self.product} x {self.quantity}"
