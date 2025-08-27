# Sales & Customer Management Module

** Sadhana Regmi 
**Project:** Python MySQL Inventory Management System  


This module handles the **Sales & Returns** and **Customer Management** parts of our team's inventory management system.

### Features:
-  **Customer Registration** - Add new customers with validation
- **Customer Management** - View and search customer records
-  **Sales Recording** - Process sales with automatic stock deduction
-  **Returns Processing** - Handle product returns with stock restoration
-  **Stock Validation** - Prevent overselling and invalid transactions
- **Error Handling** - User-friendly error messages and data protection

---

##  Files in This Module

- **`sadhana_sales_customer_management.ipynb`** - Main Jupyter notebook with all code
- **`README.md`** - This instruction file
- **`requirements.txt`** - Required Python libraries

---

##  How to Run My Code

### Step 1: Install Required Libraries
```bash
pip install mysql-connector-python pandas sqlite3
```

### Step 2: Open Jupyter Notebook
```bash
jupyter notebook sadhana_sales_customer_management.ipynb
```

### Step 3: Run the Code
1. Run **Cell 1**: Install dependencies
2. Run **Cell 2**: Import libraries
3. Run **Cell 3**: Database connection class
4. Run **Cell 4**: Initialize system
5. Continue with remaining cells in order

### Step 4: Test the System
- The notebook includes complete testing demos
- All functions are tested automatically
- Sample data is included for testing

---

##  Database Tables I Created

My code creates these tables:

1. **`customers`** - Customer information and contact details
2. **`sales`** - Sales transaction records with amounts and dates
3. **`returns`** - Return transaction records with reasons
4. **`products`** - Basic product info (works with Karuna's module)

---

##  Testing Results

**All test cases PASSED **

- **Customer Management:** 5/5 tests passed
- **Sales Recording:** 5/5 tests passed  
- **Returns Processing:** 5/5 tests passed
- **Error Handling:** All edge cases handled correctly
- **Data Validation:** Input validation working properly

---

##  Integration with Team

### My Functions Can Be Used By:
- **Karuna** - Product management connects to my sales functions
- **Gita** - Order management can use my customer and sales data
- **Punam** - Reports can pull data from my sales and returns tables

### Database Connection:
- Uses SQLite (no MySQL installation needed)
- Easy to switch to MySQL for final integration
- All tables follow team database design

---

##  What I Contributed to Team Report

**Report :** 
- Detailed transaction flow explanation
- Complete testing documentation  
- System validation results
- Integration guidelines for teammates

---

##  How to Use My Functions

### Add a Customer:
```python
customer_id = add_customer("John", "Doe", "john@email.com", "1234567890")
```

### Record a Sale:
```python
sale_id = record_sale(customer_id, product_id, quantity)
```

### Process a Return:
```python
return_id = process_return(sale_id, return_quantity, "reason")
```

### View Data:
```python
customers_df = view_customers()  # See all customers
sales_df = view_sales()          # See all sales
returns_df = view_returns()      # See all returns
```

---

##  Notes

- **Database:** Currently uses SQLite (inventory_system.db file)
- **Testing:** All functions include error handling and validation
- **Integration:** Code is modular and ready for team integration
- **Documentation:** Complete testing results included in notebook

---

## Team Project Structure

```
Our Team Project/
├── README.md (main project description)
├── requirements.txt
├── sadhana_sales_customer_management.ipynb  ← My work
├── karuna_product_management.ipynb
├── gita_orders_database.ipynb  
├── punam_reports_interface.ipynb
└── docs/
    └── team_report.md
```


