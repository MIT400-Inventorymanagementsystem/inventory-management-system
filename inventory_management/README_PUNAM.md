# Inventory Management – Reports & Analytics (Punam)

This guide lets anyone set up and run the **Reports dashboard** (KPIs + charts) and populate demo data.

## 1) Prerequisites
- **Python 3.11**
- **MySQL** server running (e.g., XAMPP → start MySQL)
- A MySQL **database and user**:
  - Database: `inventory_system`
  - User: `inventory_user`
  - Password: `Strong!Pass123`
  - Host: `localhost`
  - Grant this user all privileges on `inventory_system`

> Tip: Create these in **phpMyAdmin**: Databases → *Create*; User accounts → *Add user account* → grant on `inventory_system`.

## 2) Create and activate a virtual environment
Open a terminal **in the folder that contains `manage.py`**.

**Windows (PowerShell)**
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
# If blocked by policy: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3) Install dependencies
```bash
pip install -r requirements.txt
```

## 4) Configure database
Edit `inventory_management/settings.py`:

```python
import pymysql
pymysql.install_as_MySQLdb()

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': 'inventory_system',
    'USER': 'inventory_user',
    'PASSWORD': 'Strong!Pass123',   # change if you used a different password
    'HOST': 'localhost',
    'PORT': '3306',                 # use 3307 if you changed MySQL port
    'OPTIONS': {'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"},
  }
}

INSTALLED_APPS = [
  # ...
  'products',
  'sales',
  'reports',
]
```

Create a `static/` folder (avoids a warning):
```
project_root/
├─ manage.py
├─ static/           <-- create this if it doesn't exist
```

## 5) Migrate the schema
```bash
python manage.py makemigrations
python manage.py migrate
```

(Optional) create an admin user:
```bash
python manage.py createsuperuser
```

## 6) Seed demo data (one command)
This fills ~6 months of realistic **products, customers, sales, returns** so the dashboard is populated.

```bash
python manage.py seed_demo --reset --days 180 --customers 30
```
> The command lives at: `sales/management/commands/seed_demo.py`.

## 7) Run the site
```bash
python manage.py runserver
```
Open:
- **Reports (Punam’s dashboard):** http://127.0.0.1:8000/reports/
- Products list: http://127.0.0.1:8000/products/
- Admin: http://127.0.0.1:8000/admin/

## 8) (Optional) Streamlit + Matplotlib version
If you also want an alternative analytics view:
```bash
streamlit run reports_streamlit.py
```
Open the URL shown (usually `http://localhost:8501`).

## 9) What you’ll see on /reports/
- KPI cards: **Low-Stock Items**, **Inventory Value**, **Products In Stock**.
- Sales KPIs: **Total Revenue**, **Return Rate**, **Customers**.
- Charts:
  - Stock status (doughnut)
  - Products per category (bar)
  - Inventory value by category (bar)
  - Revenue over last 30 days (line)
  - Top products by quantity & by revenue (bar)

## 10) Troubleshooting
- **`ModuleNotFoundError: No module named 'django'`** → Activate the venv first.
- **`OperationalError: (1045) Access denied`** → DB creds in `settings.py` don’t match MySQL user/password.
- **Cannot connect to MySQL** → Make sure MySQL is running; check port (3306 vs 3307).
- **`/reports/` 404** → Add to `inventory_management/urls.py`: `path('reports/', include('reports.urls'))` and create `reports/urls.py`.
- **Admin autocomplete errors** → Ensure `products/admin.py` registers `ProductAdmin` with `search_fields`.
- **Empty charts** → Run the seeder again: `python manage.py seed_demo --reset --days 180`.

## 11) Useful commands
```bash
# start server (default 8000)
python manage.py runserver

# choose port
python manage.py runserver 8001

# open Django shell
python manage.py shell

# re-seed with different span/size
python manage.py seed_demo --reset --days 365 --customers 50
```

## 12) Expected folder layout (key parts)
```
project_root/
├─ manage.py
├─ inventory_management/
│  ├─ settings.py
│  └─ urls.py
├─ products/
│  ├─ models.py  ├─ views.py  ├─ urls.py  └─ templates/products/...
├─ sales/
│  ├─ models.py  ├─ admin.py  └─ management/commands/seed_demo.py
├─ reports/
│  ├─ views.py   ├─ urls.py   └─ templates/reports/dashboard.html
├─ static/
```