import pandas as pd
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_PATH = BASE_DIR / "data" / "raw"
PROCESSED_PATH = BASE_DIR / "data" / "processed"

PROCESSED_PATH.mkdir(parents=True, exist_ok=True)


# ============================================================
# HELPER FUNCTION
# ============================================================

def save_cleaned(df, filename):
    output_path = PROCESSED_PATH / filename
    df.to_csv(output_path, index=False)
    print(f"Saved: {filename}")
    print(f"Rows : {len(df):,}")
    print()


# ============================================================
# 1. CUSTOMERS
# ============================================================

print("=" * 60)
print("1. CLEANING CUSTOMERS")
print("=" * 60)

customers = pd.read_csv(
    RAW_PATH / "olist_customers_dataset.csv"
)

# Remove completely duplicated rows only
customers = customers.drop_duplicates()

save_cleaned(
    customers,
    "olist_customers_clean.csv"
)


# ============================================================
# 2. ORDERS
# ============================================================

print("=" * 60)
print("2. CLEANING ORDERS")
print("=" * 60)

orders = pd.read_csv(
    RAW_PATH / "olist_orders_dataset.csv"
)

# Convert date columns to datetime
date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

for column in date_columns:
    orders[column] = pd.to_datetime(
        orders[column],
        errors="coerce"
    )

# Remove exact duplicate rows
orders = orders.drop_duplicates()

save_cleaned(
    orders,
    "olist_orders_clean.csv"
)


# ============================================================
# 3. ORDER ITEMS
# ============================================================

print("=" * 60)
print("3. CLEANING ORDER ITEMS")
print("=" * 60)

order_items = pd.read_csv(
    RAW_PATH / "olist_order_items_dataset.csv"
)

# Remove exact duplicate rows only
order_items = order_items.drop_duplicates()

# Ensure numeric columns are numeric
order_items["price"] = pd.to_numeric(
    order_items["price"],
    errors="coerce"
)

order_items["freight_value"] = pd.to_numeric(
    order_items["freight_value"],
    errors="coerce"
)

save_cleaned(
    order_items,
    "olist_order_items_clean.csv"
)


# ============================================================
# 4. PAYMENTS
# ============================================================

print("=" * 60)
print("4. CLEANING PAYMENTS")
print("=" * 60)

payments = pd.read_csv(
    RAW_PATH / "olist_order_payments_dataset.csv"
)

payments = payments.drop_duplicates()

payments["payment_value"] = pd.to_numeric(
    payments["payment_value"],
    errors="coerce"
)

payments["payment_installments"] = pd.to_numeric(
    payments["payment_installments"],
    errors="coerce"
)

save_cleaned(
    payments,
    "olist_order_payments_clean.csv"
)


# ============================================================
# 5. REVIEWS
# ============================================================

print("=" * 60)
print("5. CLEANING REVIEWS")
print("=" * 60)

reviews = pd.read_csv(
    RAW_PATH / "olist_order_reviews_dataset.csv"
)

reviews = reviews.drop_duplicates()

# Convert review creation/answer dates
review_date_columns = [
    "review_creation_date",
    "review_answer_timestamp"
]

for column in review_date_columns:
    reviews[column] = pd.to_datetime(
        reviews[column],
        errors="coerce"
    )

# Review comments can legitimately be missing.
# We keep them as missing rather than inventing text.
# Review score should remain numeric.

reviews["review_score"] = pd.to_numeric(
    reviews["review_score"],
    errors="coerce"
)

save_cleaned(
    reviews,
    "olist_order_reviews_clean.csv"
)


# ============================================================
# 6. PRODUCTS
# ============================================================

print("=" * 60)
print("6. CLEANING PRODUCTS")
print("=" * 60)

products = pd.read_csv(
    RAW_PATH / "olist_products_dataset.csv"
)

products = products.drop_duplicates()

# Missing product category
products["product_category_name"] = (
    products["product_category_name"]
    .fillna("unknown")
)

# Numeric product attributes
numeric_product_columns = [
    "product_name_lenght",
    "product_description_lenght",
    "product_photos_qty",
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm"
]

for column in numeric_product_columns:
    products[column] = pd.to_numeric(
        products[column],
        errors="coerce"
    )

# Keep missing physical measurements as NaN.
# Only 2 rows are affected and replacing them with
# artificial values would introduce incorrect information.

save_cleaned(
    products,
    "olist_products_clean.csv"
)


# ============================================================
# 7. SELLERS
# ============================================================

print("=" * 60)
print("7. CLEANING SELLERS")
print("=" * 60)

sellers = pd.read_csv(
    RAW_PATH / "olist_sellers_dataset.csv"
)

sellers = sellers.drop_duplicates()

save_cleaned(
    sellers,
    "olist_sellers_clean.csv"
)


# ============================================================
# 8. GEOLOCATION
# ============================================================

print("=" * 60)
print("8. CLEANING GEOLOCATION")
print("=" * 60)

geolocation = pd.read_csv(
    RAW_PATH / "olist_geolocation_dataset.csv"
)

# Remove exact duplicate rows.
# These were identified during validation.
geolocation = geolocation.drop_duplicates()

save_cleaned(
    geolocation,
    "olist_geolocation_clean.csv"
)


# ============================================================
# 9. CATEGORY TRANSLATION
# ============================================================

print("=" * 60)
print("9. CLEANING CATEGORY TRANSLATION")
print("=" * 60)

category_translation = pd.read_csv(
    RAW_PATH / "product_category_name_translation.csv"
)

category_translation = category_translation.drop_duplicates()

save_cleaned(
    category_translation,
    "product_category_name_translation_clean.csv"
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("=" * 60)
print("CLEANING COMPLETE")
print("=" * 60)

print()
print("Cleaned datasets have been saved to:")
print(PROCESSED_PATH)

print()
print("Files created:")

for file in sorted(PROCESSED_PATH.glob("*.csv")):
    print(f"  - {file.name}")

print()
print("IMPORTANT:")
print("Original files in data/raw were NOT modified.")