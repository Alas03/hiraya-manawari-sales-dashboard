"""
generate_data.py
----------------
Creates a FAKE but realistic e-commerce dataset for "Hiraya Manawari",
a clothing store on a Shopee/Lazada-style marketplace in the Philippines.

The data is deliberately MESSY (duplicates, missing values, inconsistent
city names, mixed date formats, bad prices) so you can practice cleaning
it in Step 4.

Run it from the project folder:
    python scripts/generate_data.py

Output: 4 CSV files in data/raw/
"""

from pathlib import Path

import numpy as np
import pandas as pd

# =====================================================================
# 1. SETTINGS
# =====================================================================
SEED = 42                      # same seed = same data every time
N_CUSTOMERS = 12_000
N_ORDERS = 25_000
START_DATE = "2024-01-01"
END_DATE = "2025-12-31"

rng = np.random.default_rng(SEED)   # our random number generator

OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# =====================================================================
# 2. PRODUCTS  (category, price range, product types)
# =====================================================================
CATEGORIES = {
    "T-Shirts":             (199, 499,  ["Oversized Tee", "Graphic Tee", "Crew Neck Tee", "Polo Shirt"]),
    "Dresses":              (399, 999,  ["Floral Dress", "Midi Dress", "Summer Dress", "Wrap Dress"]),
    "Jeans & Pants":        (499, 1299, ["Skinny Jeans", "Cargo Pants", "Straight Cut Jeans", "Jogger Pants"]),
    "Hoodies & Jackets":    (599, 1499, ["Pullover Hoodie", "Zip Hoodie", "Denim Jacket", "Windbreaker"]),
    "Shorts":               (249, 599,  ["Denim Shorts", "Board Shorts", "Cotton Shorts", "Cycling Shorts"]),
    "Activewear":           (349, 899,  ["Sports Bra", "Leggings", "Dri-Fit Shirt", "Gym Shorts"]),
    "Filipiniana & Barong": (899, 2499, ["Barong Tagalog", "Baro't Saya", "Terno Dress", "Modern Filipiniana"]),
    "Accessories":          (99, 399,   ["Tote Bag", "Bucket Hat", "Scarf", "Belt"]),
}
STYLES = ["Classic", "Urban", "Sunday", "Island", "Manila", "Everyday", "Premium", "Tropical"]

product_rows = []
pid = 1
for category, (low, high, bases) in CATEGORIES.items():
    for base in bases:
        for style in rng.choice(STYLES, size=3, replace=False):
            price = int(rng.integers(low, high) // 10 * 10 + 9)   # prices end in 9, e.g. 349
            product_rows.append({
                "product_id": f"PRD-{pid:03d}",
                "product_name": f"{style} {base}",
                "category": category,
                "price": price,
            })
            pid += 1
products = pd.DataFrame(product_rows)

# =====================================================================
# 3. CUSTOMERS  (city, province, region, weight = how common)
# =====================================================================
LOCATIONS = [
    ("Quezon City",      "Metro Manila",      "NCR",                 0.09),
    ("Manila",           "Metro Manila",      "NCR",                 0.06),
    ("Makati",           "Metro Manila",      "NCR",                 0.04),
    ("Taguig",           "Metro Manila",      "NCR",                 0.04),
    ("Pasig",            "Metro Manila",      "NCR",                 0.04),
    ("Caloocan",         "Metro Manila",      "NCR",                 0.03),
    ("Antipolo",         "Rizal",             "Calabarzon",          0.04),
    ("Bacoor",           "Cavite",            "Calabarzon",          0.04),
    ("Santa Rosa",       "Laguna",            "Calabarzon",          0.03),
    ("Lipa",             "Batangas",          "Calabarzon",          0.03),
    ("Angeles",          "Pampanga",          "Central Luzon",       0.04),
    ("Malolos",          "Bulacan",           "Central Luzon",       0.03),
    ("Baguio",           "Benguet",           "CAR",                 0.02),
    ("Legazpi",          "Albay",             "Bicol",               0.02),
    ("Cebu City",        "Cebu",              "Central Visayas",     0.06),
    ("Mandaue",          "Cebu",              "Central Visayas",     0.02),
    ("Iloilo City",      "Iloilo",            "Western Visayas",     0.03),
    ("Bacolod",          "Negros Occidental", "Western Visayas",     0.03),
    ("Tacloban",         "Leyte",             "Eastern Visayas",     0.02),
    ("Davao City",       "Davao del Sur",     "Davao Region",        0.06),
    ("Cagayan de Oro",   "Misamis Oriental",  "Northern Mindanao",   0.03),
    ("Zamboanga City",   "Zamboanga del Sur", "Zamboanga Peninsula", 0.02),
    ("General Santos",   "South Cotabato",    "SOCCSKSARGEN",        0.02),
]
loc = pd.DataFrame(LOCATIONS, columns=["city", "province", "region", "weight"])

picked = rng.choice(len(loc), size=N_CUSTOMERS, p=loc["weight"] / loc["weight"].sum())
customers = loc.iloc[picked][["city", "province", "region"]].reset_index(drop=True)
customers.insert(0, "customer_id", [f"CUST-{i:05d}" for i in range(1, N_CUSTOMERS + 1)])

all_days = pd.date_range(START_DATE, END_DATE)
customers["signup_date"] = pd.to_datetime(START_DATE) - pd.to_timedelta(
    rng.integers(0, 365, N_CUSTOMERS), unit="D"
)

# =====================================================================
# 4. ORDER DATES  (some days get more orders than others)
# =====================================================================
w = 1 + 0.6 * np.arange(len(all_days)) / len(all_days)          # business grows ~60% over 2 years

day_boost = np.array([0.95, 0.90, 0.95, 1.00, 1.10, 1.15, 1.20])  # Mon..Sun
w = w * day_boost[all_days.dayofweek]

w = np.where(all_days.day.isin([15, 30]), w * 1.5, w)            # payday bump
w = np.where(all_days.month == 12, w * 1.3, w)                   # Christmas season

SALE_DAYS = {(9, 9): 4, (10, 10): 3, (11, 11): 5, (12, 12): 4}   # (month, day): boost
is_sale_day = np.zeros(len(all_days), dtype=bool)
for (m, d), boost in SALE_DAYS.items():
    mask = (all_days.month == m) & (all_days.day == d)
    w = np.where(mask, w * boost, w)
    is_sale_day |= mask

day_idx = rng.choice(len(all_days), size=N_ORDERS, p=w / w.sum())

# =====================================================================
# 5. ORDERS
# =====================================================================
orders = pd.DataFrame({
    "order_date": all_days[day_idx],
    "is_sale": is_sale_day[day_idx],
})
orders = orders.sort_values("order_date").reset_index(drop=True)
orders.insert(0, "order_id", [f"ORD-{i:06d}" for i in range(1, N_ORDERS + 1)])

# Some customers order a lot, most order once or twice
cust_weight = rng.exponential(1, N_CUSTOMERS) ** 1.5
orders["customer_id"] = rng.choice(
    customers["customer_id"], size=N_ORDERS, p=cust_weight / cust_weight.sum()
)

# Payment method
METHODS = ["COD", "GCash", "Credit Card", "ShopeePay", "Maya", "Bank Transfer"]
orders["payment_method"] = rng.choice(METHODS, size=N_ORDERS, p=[0.35, 0.30, 0.12, 0.10, 0.08, 0.05])

# Order status: COD orders get cancelled and returned more often
is_cod = (orders["payment_method"] == "COD").to_numpy()
cancel_p = np.where(is_cod, 0.20, 0.08)
return_p = np.where(is_cod, 0.08, 0.04)
u = rng.random(N_ORDERS)
orders["status"] = np.where(u < cancel_p, "Cancelled",
                   np.where(u < cancel_p + return_p, "Returned", "Completed"))

# Shipping fee depends on how far the customer's region is (in pesos)
SHIP_RANGE = {
    "NCR": (49, 79),
    "Calabarzon": (79, 119), "Central Luzon": (79, 119), "CAR": (79, 119), "Bicol": (79, 119),
    "Central Visayas": (99, 149), "Western Visayas": (99, 149), "Eastern Visayas": (99, 149),
    "Davao Region": (119, 179), "Northern Mindanao": (119, 179),
    "Zamboanga Peninsula": (119, 179), "SOCCSKSARGEN": (119, 179),
}
region_of = customers.set_index("customer_id")["region"]
order_region = orders["customer_id"].map(region_of)
low = order_region.map(lambda r: SHIP_RANGE[r][0]).to_numpy()
high = order_region.map(lambda r: SHIP_RANGE[r][1]).to_numpy()
orders["shipping_fee"] = rng.integers(low, high + 1)

# Customers can't sign up AFTER their first order
first_order = orders.groupby("customer_id")["order_date"].min()
customers["first_order"] = customers["customer_id"].map(first_order)
customers["signup_date"] = customers[["signup_date", "first_order"]].min(axis=1)
customers = customers.drop(columns="first_order")

# =====================================================================
# 6. ORDER ITEMS  (each order has 1-4 products)
# =====================================================================
n_items = rng.choice([1, 2, 3, 4], size=N_ORDERS, p=[0.55, 0.28, 0.12, 0.05])
discount = np.where(orders["is_sale"], rng.choice([0.10, 0.15, 0.20, 0.25], N_ORDERS), 0.0)

items = pd.DataFrame({
    "order_id": np.repeat(orders["order_id"].to_numpy(), n_items),
    "discount": np.repeat(discount, n_items),
})
popularity = rng.exponential(1, len(products)) ** 1.3           # some products are bestsellers
items["product_id"] = rng.choice(products["product_id"], size=len(items), p=popularity / popularity.sum())
items = items.drop_duplicates(["order_id", "product_id"]).reset_index(drop=True)
items["quantity"] = rng.choice([1, 2, 3], size=len(items), p=[0.75, 0.18, 0.07])

price_of = products.set_index("product_id")["price"]
items["unit_price"] = (items["product_id"].map(price_of) * (1 - items["discount"])).round(2)
items = items.drop(columns="discount")

orders = orders.drop(columns="is_sale")

# =====================================================================
# 7. MAKE THE DATA MESSY (so you can clean it in Step 4)
# =====================================================================

# --- orders: mixed date formats
fmt = rng.choice(["%Y-%m-%d", "%m/%d/%Y", "%d-%b-%Y"], size=len(orders), p=[0.90, 0.07, 0.03])
orders["order_date"] = [d.strftime(f) for d, f in zip(orders["order_date"], fmt)]

# --- orders: missing payment methods
orders.loc[orders.sample(300, random_state=1).index, "payment_method"] = np.nan

# --- orders: inconsistent status casing ("completed" instead of "Completed")
lower_idx = orders.sample(frac=0.04, random_state=2).index
orders.loc[lower_idx, "status"] = orders.loc[lower_idx, "status"].str.lower()

# --- orders: 150 exact duplicate rows
orders = pd.concat([orders, orders.sample(150, random_state=3)], ignore_index=True)
orders = orders.sample(frac=1, random_state=4).reset_index(drop=True)   # shuffle

# --- customers: inconsistent city names
ALIASES = {
    "Quezon City": ["QC", "quezon city"],
    "Manila": ["manila", "City of Manila"],
    "Cebu City": ["Cebu", "cebu city"],
    "Davao City": ["Davao", "davao city"],
    "Makati": ["makati city"],
}

def dirty_city(city):
    options = [city.lower(), city.upper(), f" {city} "] + ALIASES.get(city, [])
    return str(rng.choice(options))

messy = rng.random(N_CUSTOMERS) < 0.12
customers.loc[messy, "city"] = customers.loc[messy, "city"].apply(dirty_city)

# --- customers: missing provinces
customers.loc[customers.sample(150, random_state=5).index, "province"] = np.nan

# --- products: inconsistent category casing / spaces
messy_cat = rng.random(len(products)) < 0.15
products.loc[messy_cat, "category"] = products.loc[messy_cat, "category"].apply(
    lambda c: str(rng.choice([c.lower(), c.upper(), f"{c} "]))
)

# --- order_items: bad prices (zero or negative)
bad = items.sample(40, random_state=6).index
items.loc[bad[:20], "unit_price"] = 0
items.loc[bad[20:], "unit_price"] = -items.loc[bad[20:], "unit_price"]

# =====================================================================
# 8. SAVE
# =====================================================================
orders.to_csv(OUT_DIR / "orders.csv", index=False)
items.to_csv(OUT_DIR / "order_items.csv", index=False)
customers.to_csv(OUT_DIR / "customers.csv", index=False)
products.to_csv(OUT_DIR / "products.csv", index=False)

print("Done! Files saved in:", OUT_DIR)
print(f"  orders.csv       {len(orders):>7,} rows")
print(f"  order_items.csv  {len(items):>7,} rows")
print(f"  customers.csv    {len(customers):>7,} rows")
print(f"  products.csv     {len(products):>7,} rows")
