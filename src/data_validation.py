from pathlib import Path
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

DATA_PATH = Path("data/raw")


# ============================================================
# LOAD DATASETS
# ============================================================

customers = pd.read_csv(
    DATA_PATH / "olist_customers_dataset.csv"
)

orders = pd.read_csv(
    DATA_PATH / "olist_orders_dataset.csv"
)

order_items = pd.read_csv(
    DATA_PATH / "olist_order_items_dataset.csv"
)

payments = pd.read_csv(
    DATA_PATH / "olist_order_payments_dataset.csv"
)

reviews = pd.read_csv(
    DATA_PATH / "olist_order_reviews_dataset.csv"
)

products = pd.read_csv(
    DATA_PATH / "olist_products_dataset.csv"
)

sellers = pd.read_csv(
    DATA_PATH / "olist_sellers_dataset.csv"
)

geolocation = pd.read_csv(
    DATA_PATH / "olist_geolocation_dataset.csv"
)

category_translation = pd.read_csv(
    DATA_PATH / "product_category_name_translation.csv"
)


# ============================================================
# HELPER FUNCTION
# ============================================================

def print_section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


# ============================================================
# 1. DATASET ROW COUNTS
# ============================================================

print_section("1. DATASET ROW COUNTS")

datasets = {
    "Customers": customers,
    "Orders": orders,
    "Order Items": order_items,
    "Payments": payments,
    "Reviews": reviews,
    "Products": products,
    "Sellers": sellers,
    "Geolocation": geolocation,
    "Category Translation": category_translation,
}

for name, df in datasets.items():
    print(f"{name:<25}: {len(df):,}")


# ============================================================
# 2. MISSING VALUES
# ============================================================

print_section("2. MISSING VALUES")

for name, df in datasets.items():

    missing = df.isnull().sum()
    missing = missing[missing > 0]

    print(f"\n{name}")

    if missing.empty:
        print("  No missing values")
    else:
        for column, count in missing.items():
            percentage = (count / len(df)) * 100
            print(
                f"  {column}: {count:,} "
                f"({percentage:.2f}%)"
            )


# ============================================================
# 3. DUPLICATE ROWS
# ============================================================

print_section("3. DUPLICATE ROWS")

for name, df in datasets.items():

    duplicate_count = df.duplicated().sum()

    print(
        f"{name:<25}: "
        f"{duplicate_count:,} duplicate rows"
    )


# ============================================================
# 4. IMPORTANT DATA TYPES
# ============================================================

print_section("4. IMPORTANT DATA TYPES")

print("\nOrders:")

order_date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]

print(
    orders[order_date_columns].dtypes
)

print("\nOrder Items:")

print(
    order_items[
        ["price", "freight_value"]
    ].dtypes
)

print("\nPayments:")

print(
    payments[
        ["payment_value"]
    ].dtypes
)


# ============================================================
# 5. CUSTOMER VALIDATION
# ============================================================

print_section("5. CUSTOMER VALIDATION")

print(
    f"Customer rows              : "
    f"{len(customers):,}"
)

print(
    f"Unique customer_id         : "
    f"{customers['customer_id'].nunique():,}"
)

print(
    f"Unique customer_unique_id  : "
    f"{customers['customer_unique_id'].nunique():,}"
)


# ============================================================
# 6. ORDER VALIDATION
# ============================================================

print_section("6. ORDER VALIDATION")

orders_unique = orders["order_id"].nunique()

order_items_orders_unique = (
    order_items["order_id"].nunique()
)

print(
    f"Unique orders in orders table      : "
    f"{orders_unique:,}"
)

print(
    f"Unique orders in order_items table : "
    f"{order_items_orders_unique:,}"
)


# ============================================================
# 7. ORDER ITEM VALIDATION
# ============================================================

print_section("7. ORDER ITEM VALIDATION")

print(
    f"Order item rows          : "
    f"{len(order_items):,}"
)

# IMPORTANT:
# order_item_id is only unique within an order.
# Therefore we validate the combination:
# order_id + order_item_id

unique_order_item_pairs = (
    order_items[
        ["order_id", "order_item_id"]
    ]
    .drop_duplicates()
    .shape[0]
)

duplicate_order_item_pairs = (
    len(order_items) - unique_order_item_pairs
)

print(
    f"Unique (order_id + order_item_id) : "
    f"{unique_order_item_pairs:,}"
)

print(
    f"Duplicate order item combinations : "
    f"{duplicate_order_item_pairs:,}"
)


# ============================================================
# 8. REVENUE VALIDATION
# ============================================================

print_section("8. REVENUE VALIDATION")

total_product_revenue = (
    order_items["price"].sum()
)

total_freight_value = (
    order_items["freight_value"].sum()
)

print(
    f"Total product revenue : "
    f"R$ {total_product_revenue:,.2f}"
)

print(
    f"Total freight value   : "
    f"R$ {total_freight_value:,.2f}"
)


# ============================================================
# 9. PRICE VALIDATION
# ============================================================

print_section("9. PRICE VALIDATION")

negative_prices = (
    order_items["price"] < 0
).sum()

zero_prices = (
    order_items["price"] == 0
).sum()

print(
    f"Negative prices : {negative_prices:,}"
)

print(
    f"Zero prices     : {zero_prices:,}"
)


# ============================================================
# 10. FREIGHT VALIDATION
# ============================================================

print_section("10. FREIGHT VALIDATION")

negative_freight = (
    order_items["freight_value"] < 0
).sum()

print(
    f"Negative freight values : "
    f"{negative_freight:,}"
)


# ============================================================
# 11. PAYMENT VALIDATION
# ============================================================

print_section("11. PAYMENT VALIDATION")

payments_orders = payments["order_id"].nunique()

total_payment_value = (
    payments["payment_value"].sum()
)

print(
    f"Orders with payments : "
    f"{payments_orders:,}"
)

print(
    f"Total payment value  : "
    f"R$ {total_payment_value:,.2f}"
)

print("\nPayment types:")

print(
    payments["payment_type"].value_counts()
)


# ============================================================
# 12. REVIEW VALIDATION
# ============================================================

print_section("12. REVIEW VALIDATION")

valid_review_scores = [1, 2, 3, 4, 5]

invalid_review_scores = (
    ~reviews["review_score"].isin(
        valid_review_scores
    )
).sum()

print(
    f"Invalid review scores : "
    f"{invalid_review_scores:,}"
)

print("\nReview score distribution:")

print(
    reviews["review_score"].value_counts()
    .sort_index()
)


# ============================================================
# 13. PRODUCT CATEGORY VALIDATION
# ============================================================

print_section("13. PRODUCT CATEGORY VALIDATION")

products_without_category = (
    products["product_category_name"]
    .isnull()
    .sum()
)

unique_categories = (
    products["product_category_name"]
    .nunique()
)

print(
    f"Products without category : "
    f"{products_without_category:,}"
)

print(
    f"Unique product categories : "
    f"{unique_categories:,}"
)


# ============================================================
# 14. SELLER VALIDATION
# ============================================================

print_section("14. SELLER VALIDATION")

print(
    f"Seller rows       : "
    f"{len(sellers):,}"
)

print(
    f"Unique seller IDs : "
    f"{sellers['seller_id'].nunique():,}"
)


# ============================================================
# 15. DATE VALIDATION
# ============================================================

print_section("15. DATE VALIDATION")

for column in order_date_columns:

    converted_dates = pd.to_datetime(
        orders[column],
        errors="coerce"
    )

    invalid_dates = (
        converted_dates.isna()
        & orders[column].notna()
    ).sum()

    print(
        f"{column:<35}: "
        f"{invalid_dates:,} invalid"
    )


# ============================================================
# 16. RELATIONSHIP VALIDATION
# ============================================================

print_section("16. RELATIONSHIP VALIDATION")


# Orders -> Customers

orders_without_customer = (
    ~orders["customer_id"].isin(
        customers["customer_id"]
    )
).sum()

print(
    f"Orders without matching customer : "
    f"{orders_without_customer:,}"
)


# Order Items -> Orders

items_without_order = (
    ~order_items["order_id"].isin(
        orders["order_id"]
    )
).sum()

print(
    f"Items without matching order     : "
    f"{items_without_order:,}"
)


# Order Items -> Products

items_without_product = (
    ~order_items["product_id"].isin(
        products["product_id"]
    )
).sum()

print(
    f"Items without matching product   : "
    f"{items_without_product:,}"
)


# Order Items -> Sellers

items_without_seller = (
    ~order_items["seller_id"].isin(
        sellers["seller_id"]
    )
).sum()

print(
    f"Items without matching seller    : "
    f"{items_without_seller:,}"
)


# Payments -> Orders

payments_without_order = (
    ~payments["order_id"].isin(
        orders["order_id"]
    )
).sum()

print(
    f"Payments without matching order  : "
    f"{payments_without_order:,}"
)


# Reviews -> Orders

reviews_without_order = (
    ~reviews["order_id"].isin(
        orders["order_id"]
    )
).sum()

print(
    f"Reviews without matching order   : "
    f"{reviews_without_order:,}"
)


# ============================================================
# FINAL RESULT
# ============================================================

print_section("VALIDATION COMPLETE")

print(
    "\nThe validation script has completed."
)

print(
    "\nReview the results above before making "
    "any changes to the original dataset."
)