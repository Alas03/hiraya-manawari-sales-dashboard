"""
build_database.py
-----------------
Builds the SQLite database from the cleaned CSVs.

    python scripts/build_database.py

Output: data/hiraya_manawari.db
(The .db file is ignored by Git, because anyone can rebuild it with this script.)
"""

import sqlite3
from pathlib import Path

import pandas as pd

# =====================================================================
# 1. SETUP
# =====================================================================
ROOT = Path(__file__).resolve().parent.parent
CLEAN = ROOT / "data" / "cleaned"
SCHEMA = ROOT / "sql" / "schema.sql"
DB_PATH = ROOT / "data" / "hiraya_manawari.db"

if DB_PATH.exists():
    DB_PATH.unlink()              # start fresh every time

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON")   # make SQLite enforce table links

# =====================================================================
# 2. CREATE THE TABLES (runs schema.sql)
# =====================================================================
conn.executescript(SCHEMA.read_text(encoding="utf-8"))
print("Tables created from sql/schema.sql")

# =====================================================================
# 3. READ THE CLEANED CSVs
# =====================================================================
customers = pd.read_csv(CLEAN / "customers.csv")
products = pd.read_csv(CLEAN / "products.csv")
orders = pd.read_csv(CLEAN / "orders.csv")
items = pd.read_csv(CLEAN / "order_items.csv")

# =====================================================================
# 4. BUILD THE DATE TABLE (one row for every day in our data)
# =====================================================================
days = pd.date_range(orders["order_date"].min(), orders["order_date"].max())
dim_date = pd.DataFrame({
    "date_id": days.strftime("%Y-%m-%d"),
    "year": days.year,
    "month": days.month,
    "month_name": days.month_name(),
    "day_of_week": days.day_name(),
    "day_of_week_no": days.dayofweek + 1,                       # Monday = 1
    "is_weekend": (days.dayofweek >= 5).astype(int),
    "is_sale_day": ((days.month == days.day) & (days.month >= 9)).astype(int),   # 9.9, 10.10, 11.11, 12.12
    "is_payday": days.day.isin([15, 30]).astype(int),
})

# =====================================================================
# 5. LOAD THE DATA (parents first, children after)
# =====================================================================
customers.to_sql("customers", conn, if_exists="append", index=False)
products.to_sql("products", conn, if_exists="append", index=False)
dim_date.to_sql("dim_date", conn, if_exists="append", index=False)
orders.to_sql("orders", conn, if_exists="append", index=False)
items.to_sql("order_items", conn, if_exists="append", index=False)
conn.commit()

# =====================================================================
# 6. VERIFY
# =====================================================================
print("\nRows loaded:")
for table in ["customers", "products", "dim_date", "orders", "order_items"]:
    n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"  {table:<12} {n:>7,}")

broken = conn.execute("PRAGMA foreign_key_check").fetchall()
print(f"\nBroken table links: {len(broken)}  (should be 0)")

conn.close()
print(f"\nDone! Database saved to: {DB_PATH}")
