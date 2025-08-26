"""
Customer Sales Management System
Author: Sadhana 
Module: Sales & Returns, Customer Management

This module handles customer registration, sales recording with stock deduction,
and returns processing with stock restoration for an inventory management system.
"""

import sqlite3
from datetime import datetime
import pandas as pd


class CustomerSalesManager:
    """
    Customer and Sales Management System
    Handles customer registration, sales recording, and returns processing
    """
    
    def __init__(self, db_file='inventory_system.db'):
        """Initialize with SQLite database"""
        self.db_file = db_file
        self.connection = None
        
    def connect(self):
        """Connect to SQLite database"""
        try:
            self.connection = sqlite3.connect(self.db_file)
            self.connection.execute("PRAGMA foreign_keys = ON")
            print("✅ Connected to database successfully!")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def setup_tables(self):
        """Create required tables for customers, sales, returns, and products"""
        if not self.connection:
            print("❌ No database connection")
            return False
            
        cursor = self.connection.cursor()
        
        tables = {
            'customers': """
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE,
                phone TEXT,
                address TEXT,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            'products': """
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                price REAL NOT NULL,
                stock_quantity INTEGER NOT NULL DEFAULT 0
            )
            """,
            'sales': """
            CREATE TABLE IF NOT EXISTS sales (
                sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                total_amount REAL NOT NULL,
                sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            'returns': """
            CREATE TABLE IF NOT EXISTS returns (
                return_id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                return_reason TEXT,
                return_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        }
        
        try:
            for table_name, query in tables.items():
                cursor.execute(query)
                print(f"✅ {table_name.title()} table ready")
            
            self.connection.commit()
            print("🎉 All tables created successfully!")
            return True
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            return False
        finally:
            cursor.close()

    # =================
    # CUSTOMER MANAGEMENT
    # =================
    
    def add_customer(self, first_name, last_name, email=None, phone=None, address=None):
        """
        Add new customer with validation
        
        Args:
            first_name (str): Customer's first name (required)
            last_name (str): Customer's last name (required)
            email (str, optional): Customer's email address
            phone (str, optional): Customer's phone number
            address (str, optional): Customer's address
            
        Returns:
            dict: Success status and customer_id or error message
        """
        # Input validation
        if not first_name or not last_name:
            return {'success': False, 'message': 'First name and last name are required'}
        
        if email and '@' not in email:
            return {'success': False, 'message': 'Invalid email format'}
        
        cursor = self.connection.cursor()
        
        try:
            # Check if email already exists
            if email:
                cursor.execute("SELECT customer_id FROM customers WHERE email = ?", (email,))
                if cursor.fetchone():
                    return {'success': False, 'message': 'Email already exists'}
            
            # Insert new customer
            query = """
            INSERT INTO customers (first_name, last_name, email, phone, address)
            VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(query, (first_name, last_name, email, phone, address))
            self.connection.commit()
            
            customer_id = cursor.lastrowid
            return {
                'success': True,
                'message': f'Customer {first_name} {last_name} added successfully',
                'customer_id': customer_id
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Error adding customer: {str(e)}'}
        finally:
            cursor.close()
    
    def view_customers(self, customer_id=None):
        """
        View customer(s) information
        
        Args:
            customer_id (int, optional): Specific customer ID to retrieve
            
        Returns:
            dict: Customer data or error message
        """
        cursor = self.connection.cursor()
        
        try:
            if customer_id:
                cursor.execute("SELECT * FROM customers WHERE customer_id = ?", (customer_id,))
                customer = cursor.fetchone()
                if customer:
                    columns = ['customer_id', 'first_name', 'last_name', 'email', 'phone', 'address', 'registration_date']
                    return {'success': True, 'customer': dict(zip(columns, customer))}
                else:
                    return {'success': False, 'message': 'Customer not found'}
            else:
                cursor.execute("SELECT * FROM customers ORDER BY registration_date DESC")
                customers = cursor.fetchall()
                columns = ['customer_id', 'first_name', 'last_name', 'email', 'phone', 'address', 'registration_date']
                customer_list = [dict(zip(columns, customer)) for customer in customers]
                return {'success': True, 'customers': customer_list, 'count': len(customers)}
                
        except Exception as e:
            return {'success': False, 'message': f'Error retrieving customers: {str(e)}'}
        finally:
            cursor.close()
    
    def search_customers(self, search_term):
        """
        Search customers by name or email
        
        Args:
            search_term (str): Search term to match against names or email
            
        Returns:
            dict: Matching customers or error message
        """
        cursor = self.connection.cursor()
        
        try:
            query = """
            SELECT * FROM customers 
            WHERE first_name LIKE ? OR last_name LIKE ? OR email LIKE ?
            ORDER BY first_name, last_name
            """
            search_pattern = f"%{search_term}%"
            cursor.execute(query, (search_pattern, search_pattern, search_pattern))
            results = cursor.fetchall()
            
            columns = ['customer_id', 'first_name', 'last_name', 'email', 'phone', 'address', 'registration_date']
            customer_list = [dict(zip(columns, customer)) for customer in results]
            
            return {'success': True, 'customers': customer_list, 'count': len(results)}
            
        except Exception as e:
            return {'success': False, 'message': f'Search failed: {str(e)}'}
        finally:
            cursor.close()

    # =================
    # SALES MANAGEMENT
    # =================
    
    def record_sale(self, customer_id, product_id, quantity):
        """
        Record a new sale with stock validation and deduction
        
        Args:
            customer_id (int): ID of the customer making the purchase
            product_id (int): ID of the product being sold
            quantity (int): Quantity of items being sold
            
        Returns:
            dict: Sale details or error message
        """
        cursor = self.connection.cursor()
        
        try:
            # Start transaction
            cursor.execute("BEGIN")
            
            # Validate customer exists
            cursor.execute("SELECT first_name, last_name FROM customers WHERE customer_id = ?", (customer_id,))
            customer = cursor.fetchone()
            if not customer:
                self.connection.rollback()
                return {'success': False, 'message': 'Customer not found'}
            
            # Get product details and check stock
            cursor.execute("SELECT product_name, price, stock_quantity FROM products WHERE product_id = ?", (product_id,))
            product = cursor.fetchone()
            if not product:
                self.connection.rollback()
                return {'success': False, 'message': 'Product not found'}
            
            product_name, price, stock = product
            
            # Validate stock availability
            if stock < quantity:
                self.connection.rollback()
                return {
                    'success': False,
                    'message': f'Insufficient stock. Available: {stock}, Requested: {quantity}'
                }
            
            # Calculate total
            total_amount = float(price) * quantity
            
            # Record sale
            sale_query = """
            INSERT INTO sales (customer_id, product_id, quantity, unit_price, total_amount)
            VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(sale_query, (customer_id, product_id, quantity, price, total_amount))
            sale_id = cursor.lastrowid
            
            # Update stock (deduct sold quantity)
            cursor.execute("UPDATE products SET stock_quantity = stock_quantity - ? WHERE product_id = ?", 
                          (quantity, product_id))
            
            # Commit transaction
            self.connection.commit()
            
            return {
                'success': True,
                'message': 'Sale recorded successfully',
                'sale_id': sale_id,
                'customer_name': f"{customer[0]} {customer[1]}",
                'product_name': product_name,
                'quantity': quantity,
                'unit_price': float(price),
                'total_amount': total_amount,
                'remaining_stock': stock - quantity
            }
            
        except Exception as e:
            self.connection.rollback()
            return {'success': False, 'message': f'Sale failed: {str(e)}'}
        finally:
            cursor.close()

    # =================
    # RETURNS MANAGEMENT  
    # =================
    
    def process_return(self, sale_id, quantity, return_reason=""):
        """
        Process product return with stock restoration
        
        Args:
            sale_id (int): ID of the original sale
            quantity (int): Quantity of items being returned
            return_reason (str, optional): Reason for the return
            
        Returns:
            dict: Return details or error message
        """
        cursor = self.connection.cursor()
        
        try:
            # Start transaction
            cursor.execute("BEGIN")
            
            # Get sale information
            cursor.execute("""
            SELECT s.product_id, s.quantity, s.unit_price, p.product_name, p.stock_quantity
            FROM sales s
            JOIN products p ON s.product_id = p.product_id
            WHERE s.sale_id = ?
            """, (sale_id,))
            
            sale_info = cursor.fetchone()
            if not sale_info:
                self.connection.rollback()
                return {'success': False, 'message': 'Sale record not found'}
            
            product_id, sold_quantity, unit_price, product_name, current_stock = sale_info
            
            # Check how much has already been returned
            cursor.execute("SELECT COALESCE(SUM(quantity), 0) FROM returns WHERE sale_id = ?", (sale_id,))
            already_returned = cursor.fetchone()[0]
            
            available_for_return = sold_quantity - already_returned
            
            # Validate return quantity
            if quantity > available_for_return:
                self.connection.rollback()
                return {
                    'success': False,
                    'message': f'Cannot return {quantity} items. Maximum returnable: {available_for_return}'
                }
            
            # Record return
            return_query = """
            INSERT INTO returns (sale_id, product_id, quantity, return_reason)
            VALUES (?, ?, ?, ?)
            """
            cursor.execute(return_query, (sale_id, product_id, quantity, return_reason))
            return_id = cursor.lastrowid
            
            # Restore stock
            cursor.execute("UPDATE products SET stock_quantity = stock_quantity + ? WHERE product_id = ?",
                          (quantity, product_id))
            
            # Commit transaction
            self.connection.commit()
            
            return {
                'success': True,
                'message': 'Return processed successfully',
                'return_id': return_id,
                'product_name': product_name,
                'returned_quantity': quantity,
                'updated_stock': current_stock + quantity,
                'return_reason': return_reason
            }
            
        except Exception as e:
            self.connection.rollback()
            return {'success': False, 'message': f'Return processing failed: {str(e)}'}
        finally:
            cursor.close()

    # =================
    # UTILITY FUNCTIONS
    # =================
    
    def add_sample_products(self):
        """Add sample products for testing purposes"""
        cursor = self.connection.cursor()
        
        products = [
            ("Laptop", 999.99, 10),
            ("Wireless Mouse", 25.50, 50),
            ("Mechanical Keyboard", 75.00, 30),
            ("4K Monitor", 299.99, 15),
            ("USB Cable", 12.99, 100)
        ]
        
        try:
            for product in products:
                cursor.execute("""
                INSERT OR IGNORE INTO products (product_name, price, stock_quantity)
                VALUES (?, ?, ?)
                """, product)
            
            self.connection.commit()
            return {'success': True, 'message': 'Sample products added successfully'}
            
        except Exception as e:
            return {'success': False, 'message': f'Error adding products: {str(e)}'}
        finally:
            cursor.close()
    
    def get_sales_report(self, start_date=None, end_date=None):
        """
        Generate sales report for analysis
        
        Args:
            start_date (str, optional): Start date for report (YYYY-MM-DD format)
            end_date (str, optional): End date for report (YYYY-MM-DD format)
            
        Returns:
            dict: Sales report data or error message
        """
        cursor = self.connection.cursor()
        
        try:
            query = """
            SELECT s.sale_id, c.first_name, c.last_name, p.product_name, 
                   s.quantity, s.unit_price, s.total_amount, s.sale_date
            FROM sales s
            JOIN customers c ON s.customer_id = c.customer_id
            JOIN products p ON s.product_id = p.product_id
            """
            
            params = []
            if start_date and end_date:
                query += " WHERE s.sale_date BETWEEN ? AND ?"
                params = [start_date, end_date]
            
            query += " ORDER BY s.sale_date DESC"
            
            cursor.execute(query, params)
            sales = cursor.fetchall()
            
            columns = ['sale_id', 'first_name', 'last_name', 'product_name', 'quantity', 'unit_price', 'total_amount', 'sale_date']
            sales_list = [dict(zip(columns, sale)) for sale in sales]
            
            # Calculate totals
            total_sales = sum(sale['total_amount'] for sale in sales_list)
            total_transactions = len(sales_list)
            
            return {
                'success': True,
                'sales': sales_list,
                'summary': {
                    'total_transactions': total_transactions,
                    'total_sales_amount': total_sales,
                    'average_sale': total_sales / total_transactions if total_transactions > 0 else 0
                }
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Error generating report: {str(e)}'}
        finally:
            cursor.close()
    
    def close_connection(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("✅ Database connection closed")


# =================
# HELPER FUNCTIONS FOR EASY USAGE
# =================

def initialize_system():
    """Initialize the sales management system"""
    system = CustomerSalesManager()
    if system.connect():
        system.setup_tables()
        system.add_sample_products()
        return system
    else:
        return None


# =================
# TESTING FUNCTIONS
# =================

def run_basic_test():
    """Run basic functionality test"""
    print("🧪 BASIC SYSTEM TEST")
    print("=" * 30)
    
    # Initialize system
    system = initialize_system()
    if not system:
        print("❌ Failed to initialize system")
        return
    
    # Test customer management
    print("\n👥 Testing Customer Management...")
    result = system.add_customer("Test", "User", "test@example.com", "1234567890")
    print(f"Add Customer: {'✅ PASSED' if result['success'] else '❌ FAILED'}")
    
    # Test sales
    print("\n💰 Testing Sales Management...")
    if result['success']:
        customer_id = result['customer_id']
        sale_result = system.record_sale(customer_id, 1, 2)
        print(f"Record Sale: {'✅ PASSED' if sale_result['success'] else '❌ FAILED'}")
        
        # Test returns
        if sale_result['success']:
            print("\n🔄 Testing Returns Management...")
            sale_id = sale_result['sale_id']
            return_result = system.process_return(sale_id, 1, "Test return")
            print(f"Process Return: {'✅ PASSED' if return_result['success'] else '❌ FAILED'}")
    
    system.close_connection()
    print("\n✅ Basic test completed!")


if __name__ == "__main__":
    run_basic_test()