import mysql.connector
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

class ProductManager:
    def __init__(self):
        self.connection = self.create_connection()
        self.create_products_table()
    
    def create_connection(self):
        """Create database connection"""
        try:
            print("Attempting to connect to database...")
            connection = mysql.connector.connect(
                host='localhost',
                port=3306,
                user='root',
                password='',
                database='inventory_system',
                autocommit=True
            )
            print("✅ Database connection successful!")
            return connection
        except mysql.connector.Error as e:
            print(f"❌ Database connection error: {e}")
            print(f"Error code: {e.errno}")
            print(f"Error message: {e.msg}")
            return None
    
    def create_products_table(self):
        """Create products table if it doesn't exist"""
        if self.connection:
            cursor = self.connection.cursor()
            create_table_query = '''
            CREATE TABLE IF NOT EXISTS products (
                product_id INT AUTO_INCREMENT PRIMARY KEY,
                product_name VARCHAR(255) NOT NULL UNIQUE,
                category VARCHAR(100),
                price DECIMAL(10, 2) NOT NULL,
                stock_quantity INT DEFAULT 0,
                min_threshold INT DEFAULT 10,
                description TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            '''
            cursor.execute(create_table_query)
            self.connection.commit()
            cursor.close()
    
    # CRUD Operations
    
    def add_product(self, product_name, category, price, stock_quantity, min_threshold=10, description=""):
        """Add a new product to inventory"""
        if not self.connection:
            return False, "Database connection failed"
        
        try:
            cursor = self.connection.cursor()
            
            # Check if product already exists
            check_query = "SELECT product_id FROM products WHERE product_name = %s"
            cursor.execute(check_query, (product_name,))
            
            if cursor.fetchone():
                cursor.close()
                return False, "Product already exists"
            
            # Insert new product
            insert_query = '''
            INSERT INTO products (product_name, category, price, stock_quantity, min_threshold, description)
            VALUES (%s, %s, %s, %s, %s, %s)
            '''
            values = (product_name, category, price, stock_quantity, min_threshold, description)
            cursor.execute(insert_query, values)
            self.connection.commit()
            cursor.close()
            
            return True, "Product added successfully"
            
        except mysql.connector.Error as e:
            return False, f"Error adding product: {e}"
    
    def update_product(self, product_id, **kwargs):
        """Update product information"""
        if not self.connection:
            return False, "Database connection failed"
        
        try:
            cursor = self.connection.cursor()
            
            # Build update query dynamically based on provided fields
            update_fields = []
            values = []
            
            for field, value in kwargs.items():
                if field in ['product_name', 'category', 'price', 'stock_quantity', 'min_threshold', 'description']:
                    update_fields.append(f"{field} = %s")
                    values.append(value)
            
            if not update_fields:
                cursor.close()
                return False, "No valid fields to update"
            
            values.append(product_id)
            update_query = f"UPDATE products SET {', '.join(update_fields)} WHERE product_id = %s"
            
            cursor.execute(update_query, values)
            self.connection.commit()
            
            if cursor.rowcount > 0:
                cursor.close()
                return True, "Product updated successfully"
            else:
                cursor.close()
                return False, "Product not found"
                
        except mysql.connector.Error as e:
            return False, f"Error updating product: {e}"
    
    def delete_product(self, product_id):
        """Delete a product from inventory"""
        if not self.connection:
            return False, "Database connection failed"
        
        try:
            cursor = self.connection.cursor()
            
            # Check if product exists
            check_query = "SELECT product_name FROM products WHERE product_id = %s"
            cursor.execute(check_query, (product_id,))
            product = cursor.fetchone()
            
            if not product:
                cursor.close()
                return False, "Product not found"
            
            # Delete product
            delete_query = "DELETE FROM products WHERE product_id = %s"
            cursor.execute(delete_query, (product_id,))
            self.connection.commit()
            cursor.close()
            
            return True, f"Product '{product[0]}' deleted successfully"
            
        except mysql.connector.Error as e:
            return False, f"Error deleting product: {e}"
    
    def search_products(self, search_term="", category="", min_price=None, max_price=None):
        """Search and filter products"""
        if not self.connection:
            return []
        
        try:
            cursor = self.connection.cursor()
            
            # Build search query
            conditions = []
            values = []
            
            if search_term:
                conditions.append("product_name LIKE %s")
                values.append(f"%{search_term}%")
            
            if category:
                conditions.append("category = %s")
                values.append(category)
            
            if min_price is not None:
                conditions.append("price >= %s")
                values.append(min_price)
            
            if max_price is not None:
                conditions.append("price <= %s")
                values.append(max_price)
            
            query = "SELECT * FROM products"
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            cursor.execute(query, values)
            products = cursor.fetchall()
            cursor.close()
            
            return products
            
        except mysql.connector.Error as e:
            print(f"Error searching products: {e}")
            return []
    
    def get_all_products(self):
        """Get all products"""
        return self.search_products()
    
    # Low-Stock Alert System
    
    def check_low_stock(self):
        """Find products with stock below minimum threshold"""
        if not self.connection:
            return []
        
        try:
            cursor = self.connection.cursor()
            query = "SELECT * FROM products WHERE stock_quantity <= min_threshold"
            cursor.execute(query)
            low_stock_products = cursor.fetchall()
            cursor.close()
            
            return low_stock_products
            
        except mysql.connector.Error as e:
            print(f"Error checking low stock: {e}")
            return []
    
    def get_alert_count(self):
        """Get count of products with low stock"""
        low_stock_products = self.check_low_stock()
        return len(low_stock_products)
    
    def update_threshold(self, product_id, new_threshold):
        """Update minimum stock threshold for a product"""
        return self.update_product(product_id, min_threshold=new_threshold)


class ProductManagementGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Product Management System - Karuna's Part")
        self.root.geometry("1000x600")
        
        self.product_manager = ProductManager()
        self.create_widgets()
        self.refresh_product_list()
    
    def create_widgets(self):
        """Create the GUI interface"""
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Product Management & Low-Stock Alerts", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Alert Panel
        self.create_alert_panel(main_frame)
        
        # Product Management Panel
        self.create_product_panel(main_frame)
        
        # Product List
        self.create_product_list(main_frame)
    
    def create_alert_panel(self, parent):
        """Create low-stock alert panel"""
        alert_frame = ttk.LabelFrame(parent, text="Low Stock Alerts", padding="5")
        alert_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.alert_label = ttk.Label(alert_frame, text="Checking alerts...", 
                                    foreground="red", font=('Arial', 10, 'bold'))
        self.alert_label.grid(row=0, column=0, padx=5)
        
        ttk.Button(alert_frame, text="View Low Stock Items", 
                  command=self.show_low_stock_items).grid(row=0, column=1, padx=5)
    
    def create_product_panel(self, parent):
        """Create product management controls"""
        control_frame = ttk.LabelFrame(parent, text="Product Management", padding="5")
        control_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Buttons
        ttk.Button(control_frame, text="Add Product", 
                  command=self.add_product_dialog).grid(row=0, column=0, padx=5)
        ttk.Button(control_frame, text="Update Product", 
                  command=self.update_product_dialog).grid(row=0, column=1, padx=5)
        ttk.Button(control_frame, text="Delete Product", 
                  command=self.delete_product_dialog).grid(row=0, column=2, padx=5)
        
        # Search
        ttk.Label(control_frame, text="Search:").grid(row=1, column=0, padx=5, pady=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(control_frame, textvariable=self.search_var)
        search_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(control_frame, text="Search", 
                  command=self.search_products).grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(control_frame, text="Show All", 
                  command=self.refresh_product_list).grid(row=1, column=3, padx=5, pady=5)
    
    def create_product_list(self, parent):
        """Create product list display"""
        list_frame = ttk.LabelFrame(parent, text="Product List", padding="5")
        list_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Treeview for product list
        columns = ('ID', 'Name', 'Category', 'Price', 'Stock', 'Threshold', 'Status')
        self.product_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Define column headings
        for col in columns:
            self.product_tree.heading(col, text=col)
            self.product_tree.column(col, width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.product_tree.yview)
        self.product_tree.configure(yscrollcommand=scrollbar.set)
        
        self.product_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
    
    def refresh_product_list(self):
        """Refresh the product list display"""
        # Clear existing items
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        # Get all products
        products = self.product_manager.get_all_products()
        
        # Add products to tree
        for product in products:
            product_id, name, category, price, stock, threshold, desc, created, updated = product
            
            # Determine status
            if stock <= 0:
                status = "OUT OF STOCK"
                tag = "out_of_stock"
            elif stock <= threshold:
                status = "LOW STOCK"
                tag = "low_stock"
            else:
                status = "IN STOCK"
                tag = "in_stock"
            
            self.product_tree.insert('', tk.END, 
                                   values=(product_id, name, category, f"${price:.2f}", 
                                          stock, threshold, status),
                                   tags=(tag,))
        
        # Configure tags for color coding
        self.product_tree.tag_configure('out_of_stock', background='#ffcccc')
        self.product_tree.tag_configure('low_stock', background='#fff3cd')
        self.product_tree.tag_configure('in_stock', background='#d4edda')
        
        # Update alert display
        self.update_alert_display()
    
    def update_alert_display(self):
        """Update the alert display"""
        alert_count = self.product_manager.get_alert_count()
        if alert_count > 0:
            self.alert_label.config(text=f"⚠️ {alert_count} products need restocking!", 
                                   foreground="red")
        else:
            self.alert_label.config(text="✅ All products are well stocked", 
                                   foreground="green")
    
    def add_product_dialog(self):
        """Show dialog to add new product"""
        dialog = ProductDialog(self.root, "Add Product", self.product_manager)
        if dialog.result:
            self.refresh_product_list()
    
    def update_product_dialog(self):
        """Show dialog to update product"""
        selected = self.product_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a product to update.")
            return
        
        product_id = self.product_tree.item(selected[0])['values'][0]
        dialog = ProductDialog(self.root, "Update Product", self.product_manager, product_id)
        if dialog.result:
            self.refresh_product_list()
    
    def delete_product_dialog(self):
        """Delete selected product"""
        selected = self.product_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a product to delete.")
            return
        
        product_values = self.product_tree.item(selected[0])['values']
        product_id, product_name = product_values[0], product_values[1]
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete '{product_name}'?"):
            success, message = self.product_manager.delete_product(product_id)
            if success:
                messagebox.showinfo("Success", message)
                self.refresh_product_list()
            else:
                messagebox.showerror("Error", message)
    
    def search_products(self):
        """Search products based on search term"""
        search_term = self.search_var.get().strip()
        if not search_term:
            self.refresh_product_list()
            return
        
        # Clear existing items
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        # Search products
        products = self.product_manager.search_products(search_term=search_term)
        
        # Add filtered products to tree
        for product in products:
            product_id, name, category, price, stock, threshold, desc, created, updated = product
            
            if stock <= 0:
                status = "OUT OF STOCK"
                tag = "out_of_stock"
            elif stock <= threshold:
                status = "LOW STOCK"
                tag = "low_stock"
            else:
                status = "IN STOCK"
                tag = "in_stock"
            
            self.product_tree.insert('', tk.END, 
                                   values=(product_id, name, category, f"${price:.2f}", 
                                          stock, threshold, status),
                                   tags=(tag,))
        
        # Configure tags
        self.product_tree.tag_configure('out_of_stock', background='#ffcccc')
        self.product_tree.tag_configure('low_stock', background='#fff3cd')
        self.product_tree.tag_configure('in_stock', background='#d4edda')
    
    def show_low_stock_items(self):
        """Show only low stock items"""
        # Clear existing items
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        # Get low stock products
        low_stock_products = self.product_manager.check_low_stock()
        
        if not low_stock_products:
            messagebox.showinfo("No Low Stock", "All products are well stocked!")
            self.refresh_product_list()
            return
        
        # Add low stock products to tree
        for product in low_stock_products:
            product_id, name, category, price, stock, threshold, desc, created, updated = product
            
            if stock <= 0:
                status = "OUT OF STOCK"
                tag = "out_of_stock"
            else:
                status = "LOW STOCK"
                tag = "low_stock"
            
            self.product_tree.insert('', tk.END, 
                                   values=(product_id, name, category, f"${price:.2f}", 
                                          stock, threshold, status),
                                   tags=(tag,))
        
        # Configure tags
        self.product_tree.tag_configure('out_of_stock', background='#ffcccc')
        self.product_tree.tag_configure('low_stock', background='#fff3cd')


class ProductDialog:
    def __init__(self, parent, title, product_manager, product_id=None):
        self.product_manager = product_manager
        self.product_id = product_id
        self.result = False
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx()+50, parent.winfo_rooty()+50))
        
        self.create_form()
        
        if self.product_id:
            self.load_product_data()
    
    def create_form(self):
        """Create the product form"""
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Form fields
        ttk.Label(frame, text="Product Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.name_var, width=30).grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="Category:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.category_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.category_var, width=30).grid(row=1, column=1, pady=5)
        
        ttk.Label(frame, text="Price ($):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.price_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.price_var, width=30).grid(row=2, column=1, pady=5)
        
        ttk.Label(frame, text="Stock Quantity:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.stock_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.stock_var, width=30).grid(row=3, column=1, pady=5)
        
        ttk.Label(frame, text="Min Threshold:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.threshold_var = tk.StringVar(value="10")
        ttk.Entry(frame, textvariable=self.threshold_var, width=30).grid(row=4, column=1, pady=5)
        
        ttk.Label(frame, text="Description:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.description_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.description_var, width=30).grid(row=5, column=1, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def load_product_data(self):
        """Load existing product data for update"""
        products = self.product_manager.search_products()
        for product in products:
            if product[0] == self.product_id:
                self.name_var.set(product[1])
                self.category_var.set(product[2])
                self.price_var.set(str(product[3]))
                self.stock_var.set(str(product[4]))
                self.threshold_var.set(str(product[5]))
                self.description_var.set(product[6] or "")
                break
    
    def save_product(self):
        """Save the product"""
        try:
            name = self.name_var.get().strip()
            category = self.category_var.get().strip()
            price = float(self.price_var.get())
            stock = int(self.stock_var.get())
            threshold = int(self.threshold_var.get())
            description = self.description_var.get().strip()
            
            if not name or price < 0 or stock < 0 or threshold < 0:
                messagebox.showerror("Invalid Input", "Please fill all required fields with valid values.")
                return
            
            if self.product_id:
                # Update existing product
                success, message = self.product_manager.update_product(
                    self.product_id,
                    product_name=name,
                    category=category,
                    price=price,
                    stock_quantity=stock,
                    min_threshold=threshold,
                    description=description
                )
            else:
                # Add new product
                success, message = self.product_manager.add_product(
                    name, category, price, stock, threshold, description
                )
            
            if success:
                messagebox.showinfo("Success", message)
                self.result = True
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", message)
                
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for price, stock, and threshold.")


def main():
    root = tk.Tk()
    app = ProductManagementGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()