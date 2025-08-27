from decimal import Decimal
import random
import datetime
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import models
from django.utils import timezone

from products.models import Product
from sales.models import Customer, Sale, Return


PRODUCTS = [
    # name, category, price, initial_stock, min_threshold, description
    ("Gaming Laptop",          "Electronics",     Decimal("1299.99"),  80,  5, "High-performance gaming laptop"),
    ("Wireless Keyboard",      "Electronics",     Decimal("79.99"),   120,  8, "Mechanical wireless keyboard"),
    ("Office Pen",             "Stationery",      Decimal("2.50"),    300, 10, "Blue ballpoint pen"),
    ("Printer Paper (A4 500)", "Office Supplies", Decimal("15.99"),   150,  5, "A4 white copy paper"),
    ("Noise-cancel Headphones","Electronics",     Decimal("199.00"),   90,  6, "Over-ear ANC"),
    ("USB-C Cable",            "Electronics",     Decimal("9.99"),    400, 20, "1m USB-C cable"),
    ("Desk Chair",             "Home/Office",     Decimal("149.00"),   60,  4, "Ergonomic chair"),
    ("Notebook A5",            "Stationery",      Decimal("4.00"),    250, 20, "A5 ruled notebook"),
    ("Desk Lamp",              "Home/Office",     Decimal("35.00"),   100,  6, "LED lamp"),
    ("External SSD 1TB",       "Electronics",     Decimal("129.00"),   70,  5, "USB 3.2 NVMe"),
    ("Coffee Beans 1kg",       "Grocery",         Decimal("18.50"),    90, 10, "100% Arabica"),
    ("Water Bottle 500ml",     "Grocery",         Decimal("3.20"),    300, 30, "Reusable bottle"),
]

FIRST = ["Alex","Sam","Chris","Riya","Aman","Leena","John","Priya","Karan","Maya",
         "Nikhil","Anita","Sara","Vikram","Ivy","Noah","Ava","Liam","Emma","Olivia"]
LAST  = ["Shah","Patel","Singh","Khan","Roy","Das","Nair","Joshi","Gupta","Mehta",
         "Brown","Lee","Chen","Garcia","Smith"]


class Command(BaseCommand):
    help = "Seed demo data: products, customers, ~N days of sales, periodic returns and restocks."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=180, help="How many days back to generate (default 180).")
        parser.add_argument("--customers", type=int, default=30, help="Number of customers to create (default 30).")
        parser.add_argument("--seed", type=int, default=7, help="Random seed for reproducible data (default 7).")
        parser.add_argument("--reset", action="store_true",
                            help="Delete existing Sales/Returns before seeding (Products are kept/reset to baseline).")
        parser.add_argument("--no-restock", action="store_true",
                            help="Disable periodic restocking (more items will go low/out-of-stock).")

    def handle(self, *args, **opts):
        random.seed(opts["seed"])
        days = opts["days"]
        num_customers = opts["customers"]
        do_reset = opts["reset"]
        do_restock = not opts["no_restock"]

        # Optional reset for a clean demo
        if do_reset:
            self.stdout.write(self.style.WARNING("Resetting Sales and Returns…"))
            Return.objects.all().delete()
            Sale.objects.all().delete()

        # Ensure products exist and reset their baseline values
        self.stdout.write("Creating/updating baseline products…")
        product_objs = []
        for name, cat, price, stock, threshold, desc in PRODUCTS:
            p, _ = Product.objects.get_or_create(
                product_name=name,
                defaults={
                    "category": cat,
                    "price": price,
                    "stock_quantity": stock,
                    "min_threshold": threshold,
                    "description": desc,
                },
            )
            p.category = cat
            p.price = price
            p.stock_quantity = stock
            p.min_threshold = threshold
            p.description = desc
            p.save()
            product_objs.append(p)

        # Customers
        self.stdout.write(f"Ensuring {num_customers} customers…")
        customers = []
        for i in range(num_customers):
            fn = random.choice(FIRST)
            ln = random.choice(LAST)
            email = f"{fn.lower()}.{ln.lower()}{i}@example.com"
            c, _ = Customer.objects.get_or_create(email=email, defaults={"first_name": fn, "last_name": ln})
            customers.append(c)

        # Generate sales/returns across a date range
        start_date = timezone.now().date() - timedelta(days=days)
        today = timezone.now().date()
        span = (today - start_date).days

        sale_count = 0
        return_count = 0

        self.stdout.write(f"Generating sales/returns from {start_date} to {today}…")

        for d in range(span + 1):
            day = start_date + timedelta(days=d)

            # periodic restock every 14 days to keep inventory moving
            if do_restock and d % 14 == 0:
                for p in random.sample(product_objs, k=min(5, len(product_objs))):
                    add = random.randint(10, 60)
                    Product.objects.filter(pk=p.pk).update(
                        stock_quantity=models.F("stock_quantity") + add
                    )

            # 0–6 sales this day
            for _ in range(random.randint(0, 6)):
                p = random.choice(product_objs)
                qty = random.randint(1, 5)

                p.refresh_from_db(fields=["stock_quantity", "price"])
                if p.stock_quantity < qty:
                    continue

                cust = random.choice(customers)
                sale_time = datetime.time(hour=random.randint(9, 19), minute=random.choice([0, 15, 30, 45]))
                sale_dt = timezone.make_aware(datetime.datetime.combine(day, sale_time))

                s = Sale(customer=cust, product=p, quantity=qty, unit_price=p.price, sale_date=sale_dt)
                try:
                    s.save()  # Sale.save() adjusts stock & total_amount atomically
                    sale_count += 1
                except Exception:
                    continue

                # ~12% of sales get a small return within 1–15 days
                if random.random() < 0.12:
                    r_qty = random.randint(1, qty)
                    r_day = min(day + timedelta(days=random.randint(1, 15)), today)
                    r_dt = timezone.make_aware(datetime.datetime.combine(r_day, datetime.time(12, 0)))
                    try:
                        Return(
                            sale=s,
                            product=p,
                            quantity=r_qty,
                            return_reason=random.choice(["Damaged", "Wrong item", "Changed mind", "Defective"]),
                            return_date=r_dt,
                        ).save()  # Return.save() restores stock atomically
                        return_count += 1
                    except Exception:
                        pass

        self.stdout.write(self.style.SUCCESS(
            f"Seed complete → Products: {Product.objects.count()}, "
            f"Customers: {Customer.objects.count()}, Sales: {sale_count}, Returns: {return_count}"
        ))
