"""
clean_data.py
-------------
Cleans the messy raw CSVs from data/raw/ and saves trustworthy versions
to data/cleaned/. Also writes a cleaning log to docs/cleaning_log.md.

Run it from the project folder:
    python scripts/clean_data.py

Rule of the job: NEVER edit the raw files. Always clean a copy.
"""

from pathlib import Path

import pandas as pd

# =====================================================================
# 0. SETUP
# =====================================================================
ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
CLEAN = ROOT / "data" / "cleaned"
DOCS = ROOT / "docs"
CLEAN.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(exist_ok=True)

log = []   # every fix gets recorded here


def record(table, issue, rows, fix):
    """Save one line in the cleaning log and print it."""
    log.append({"table": table, "issue": issue, "rows": int(rows), "fix": fix})
    print(f"[{table}] {issue}: {int(rows):,} rows -> {fix}")


# =====================================================================
# 1. LOAD THE RAW DATA
# =====================================================================
orders = pd.read_csv(RAW / "orders.csv")
items = pd.read_csv(RAW / "order_items.csv")
customers = pd.read_csv(RAW / "customers.csv")
products = pd.read_csv(RAW / "products.csv")

print("Loaded raw data:")
print(f"  orders {len(orders):,} | items {len(items):,} | "
      f"customers {len(customers):,} | products {len(products):,}\n")

# =====================================================================
# 2. CLEAN ORDERS
# =====================================================================

# 2a. Exact duplicate rows -> keep one copy
n = orders.duplicated().sum()
orders = orders.drop_duplicates().reset_index(drop=True)
record("orders", "Duplicate orders", n, "Removed duplicate rows, kept first copy")

# 2b. Mixed date formats -> one real date type
#     Try each known format; whichever works fills in the date.
raw_dates = orders["order_date"]
d_iso = pd.to_datetime(raw_dates, format="%Y-%m-%d", errors="coerce")   # 2025-07-04
d_us = pd.to_datetime(raw_dates, format="%m/%d/%Y", errors="coerce")    # 07/04/2025
d_txt = pd.to_datetime(raw_dates, format="%d-%b-%Y", errors="coerce")   # 04-Jul-2025
orders["order_date"] = d_iso.fillna(d_us).fillna(d_txt)
assert orders["order_date"].notna().all(), "Some dates could not be parsed!"
record("orders", "Mixed date formats", d_iso.isna().sum(),
       "Parsed 3 formats into one YYYY-MM-DD date")

# 2c. Status casing ("completed" -> "Completed")
new_status = orders["status"].str.strip().str.title()
record("orders", "Inconsistent status casing", (new_status != orders["status"]).sum(),
       "Trimmed spaces and applied Title Case")
orders["status"] = new_status

# 2d. Missing payment method -> we can't guess it, so label it honestly
n = orders["payment_method"].isna().sum()
orders["payment_method"] = orders["payment_method"].fillna("Unknown")
record("orders", "Missing payment_method", n, "Filled with 'Unknown'")

# =====================================================================
# 3. CLEAN CUSTOMERS
# =====================================================================

# 3a. Inconsistent city names -> one official spelling each
CITIES = [
    "Quezon City", "Manila", "Makati", "Taguig", "Pasig", "Caloocan",
    "Antipolo", "Bacoor", "Santa Rosa", "Lipa", "Angeles", "Malolos",
    "Baguio", "Legazpi", "Cebu City", "Mandaue", "Iloilo City", "Bacolod",
    "Tacloban", "Davao City", "Cagayan de Oro", "Zamboanga City", "General Santos",
]
ALIASES = {                      # nicknames -> official name
    "qc": "Quezon City",
    "city of manila": "Manila",
    "cebu": "Cebu City",
    "davao": "Davao City",
    "makati city": "Makati",
}
city_lookup = {c.lower(): c for c in CITIES}
city_lookup.update(ALIASES)

new_city = customers["city"].str.strip().str.lower().map(city_lookup)
assert new_city.notna().all(), "Found a city name I don't recognize!"
record("customers", "Inconsistent city names", (new_city != customers["city"]).sum(),
       "Trimmed, lower-cased, then mapped to one official spelling (QC -> Quezon City)")
customers["city"] = new_city

# 3b. Missing province -> recover it from the city (each city has one province)
city_to_province = (
    customers.dropna(subset=["province"])
    .groupby("city")["province"]
    .agg(lambda s: s.mode()[0])
)
n = customers["province"].isna().sum()
customers["province"] = customers["province"].fillna(customers["city"].map(city_to_province))
assert customers["province"].notna().all()
record("customers", "Missing province", n, "Recovered from the customer's city")

# 3c. Dates
customers["signup_date"] = pd.to_datetime(customers["signup_date"])

# =====================================================================
# 4. CLEAN PRODUCTS
# =====================================================================
new_cat = products["category"].str.strip().str.title()
record("products", "Inconsistent category text", (new_cat != products["category"]).sum(),
       "Trimmed spaces and applied Title Case")
products["category"] = new_cat

# =====================================================================
# 5. CLEAN ORDER ITEMS
# =====================================================================
# Zero or negative prices are impossible -> restore from the product's list price
bad = items["unit_price"] <= 0
list_price = items["product_id"].map(products.set_index("product_id")["price"])
items.loc[bad, "unit_price"] = list_price[bad]
record("order_items", "Zero or negative unit_price", bad.sum(),
       "Replaced with the product's list price (sale discount unknown for these rows)")

# =====================================================================
# 6. INTEGRITY CHECKS (do the tables still connect properly?)
# =====================================================================
print("\nIntegrity checks (all should be 0):")
checks = {
    "duplicate order_ids": orders["order_id"].duplicated().sum(),
    "items pointing to missing orders": (~items["order_id"].isin(orders["order_id"])).sum(),
    "items pointing to missing products": (~items["product_id"].isin(products["product_id"])).sum(),
    "orders pointing to missing customers": (~orders["customer_id"].isin(customers["customer_id"])).sum(),
    "non-positive unit prices": (items["unit_price"] <= 0).sum(),
}
for name, value in checks.items():
    print(f"  {name}: {value}")

# =====================================================================
# 7. SAVE CLEANED FILES + CLEANING LOG
# =====================================================================
orders.to_csv(CLEAN / "orders.csv", index=False)
items.to_csv(CLEAN / "order_items.csv", index=False)
customers.to_csv(CLEAN / "customers.csv", index=False)
products.to_csv(CLEAN / "products.csv", index=False)

lines = [
    "# Cleaning Log",
    "",
    "Every problem found in the raw data and how it was fixed.",
    "",
    "| Table | Issue | Rows affected | Fix |",
    "|---|---|---:|---|",
]
for row in log:
    lines.append(f"| {row['table']} | {row['issue']} | {row['rows']:,} | {row['fix']} |")
(DOCS / "cleaning_log.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

print(f"\nDone! Cleaned files saved in: {CLEAN}")
print(f"Cleaning log saved to: {DOCS / 'cleaning_log.md'}")
print(f"  orders {len(orders):,} | items {len(items):,} | "
      f"customers {len(customers):,} | products {len(products):,}")
