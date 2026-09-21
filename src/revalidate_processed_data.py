from pathlib import Path
import pandas as pd


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_PATH = BASE_DIR / "data" / "raw"
PROCESSED_PATH = BASE_DIR / "data" / "processed"


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def load_processed(filename):
    return pd.read_csv(PROCESSED_PATH / filename)


# ============================================================
# LOAD CLEANED DATA
# ============================================================

customers = load_processed("olist_customers_clean.csv")
orders = load_processed("olist_orders_clean.csv")
order_items = load_processed("olist_order_items_clean.csv")
payments = load_processed("olist_order_payments_clean.csv")
reviews = load_processed("olist_order_reviews_clean.csv")
products = load_processed("olist_products_clean.csv")
sellers = load_processed("olist_sellers_clean.csv")
geolocation = load_processed("olist_geolocation_clean.csv")
category_translation = load_processed(
    "product_category_name_translation_clean.csv"
)


# ============================================================
# 1. ROW COUNT VALIDATION
# ============================================================

section("1. PROCESSED DATASET ROW COUNTS")

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
# 2. DUPLICATE VALIDATION
# ============================================================

section("2. DUPLICATE VALIDATION")

for name, df in datasets.items():

    duplicates = df.duplicated().sum()

    status = "PASS" if duplicates == 0 else "CHECK"

    print(
        f"{name:<25}: "
        f"{duplicates:,} duplicate rows "
        f"[{status}]"
    )


# ============================================================
# 3. MISSING VALUE VALIDATION
# ============================================================

section("3. MISSING VALUE VALIDATION")

for name, df in datasets.items():

    missing_total = df.isnull().sum().sum()

    print(
        f"{name:<25}: "
        f"{missing_total:,} missing values"
    )

    if missing_total > 0:

        missing = df.isnull().sum()
        missing = missing[missing > 0]

        for column, count in missing.items():
            percentage = count / len(df) * 100

            print(
                f"    {column}: "
                f"{count:,} ({percentage:.2f}%)"
            )


# ============================================================
# 4. ORDER DATE VALIDATION
# ============================================================

section("4. ORDER DATE VALIDATION")

date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]

for column in date_columns:

    converted = pd.to_datetime(
        orders[column],
        errors="coerce"
    )

    invalid = (
        converted.isna()
        & orders[column].notna()
    ).sum()

    print(
        f"{column:<35}: "
        f"{invalid:,} invalid"
    )


# ============================================================
# 5. ORDER ITEM VALIDATION
# ============================================================

section("5. ORDER ITEM VALIDATION")

unique_pairs = (
    order_items[
        ["order_id", "order_item_id"]
    ]
    .drop_duplicates()
    .shape[0]
)

duplicate_pairs = (
    len(order_items) - unique_pairs
)

print(
    f"Order item rows                  : "
    f"{len(order_items):,}"
)

print(
    f"Unique order + item combinations : "
    f"{unique_pairs:,}"
)

print(
    f"Duplicate combinations           : "
    f"{duplicate_pairs:,}"
)


# ============================================================
# 6. PRICE VALIDATION
# ============================================================

section("6. PRICE VALIDATION")

negative_prices = (
    order_items["price"] < 0
).sum()

zero_prices = (
    order_items["price"] == 0
).sum()

print(
    f"Negative prices : "
    f"{negative_prices:,}"
)

print(
    f"Zero prices     : "
    f"{zero_prices:,}"
)


# ============================================================
# 7. FREIGHT VALIDATION
# ============================================================

section("7. FREIGHT VALIDATION")

negative_freight = (
    order_items["freight_value"] < 0
).sum()

print(
    f"Negative freight values : "
    f"{negative_freight:,}"
)


# ============================================================
# 8. PAYMENT VALIDATION
# ============================================================

section("8. PAYMENT VALIDATION")

negative_payments = (
    payments["payment_value"] < 0
).sum()

zero_payments = (
    payments["payment_value"] == 0
).sum()

print(
    f"Negative payment values : "
    f"{negative_payments:,}"
)

print(
    f"Zero payment values     : "
    f"{zero_payments:,}"
)


# ============================================================
# 9. REVIEW VALIDATION
# ============================================================

section("9. REVIEW VALIDATION")

valid_scores = [1, 2, 3, 4, 5]

invalid_scores = (
    ~reviews["review_score"].isin(valid_scores)
).sum()

print(
    f"Invalid review scores : "
    f"{invalid_scores:,}"
)

print("\nReview score distribution:")

print(
    reviews["review_score"]
    .value_counts()
    .sort_index()
)


# ============================================================
# 10. PRODUCT CATEGORY VALIDATION
# ============================================================

section("10. PRODUCT CATEGORY VALIDATION")

missing_categories = (
    products["product_category_name"]
    .isnull()
    .sum()
)

unknown_categories = (
    products["product_category_name"]
    .eq("unknown")
    .sum()
)

print(
    f"Missing categories : "
    f"{missing_categories:,}"
)

print(
    f"Unknown categories : "
    f"{unknown_categories:,}"
)


# ============================================================
# 11. RELATIONSHIP VALIDATION
# ============================================================

section("11. RELATIONSHIP VALIDATION")


orders_without_customer = (
    ~orders["customer_id"].isin(
        customers["customer_id"]
    )
).sum()

items_without_order = (
    ~order_items["order_id"].isin(
        orders["order_id"]
    )
).sum()

items_without_product = (
    ~order_items["product_id"].isin(
        products["product_id"]
    )
).sum()

items_without_seller = (
    ~order_items["seller_id"].isin(
        sellers["seller_id"]
    )
).sum()

payments_without_order = (
    ~payments["order_id"].isin(
        orders["order_id"]
    )
).sum()

reviews_without_order = (
    ~reviews["order_id"].isin(
        orders["order_id"]
    )
).sum()


print(
    f"Orders without matching customer : "
    f"{orders_without_customer:,}"
)

print(
    f"Items without matching order     : "
    f"{items_without_order:,}"
)

print(
    f"Items without matching product   : "
    f"{items_without_product:,}"
)

print(
    f"Items without matching seller    : "
    f"{items_without_seller:,}"
)

print(
    f"Payments without matching order  : "
    f"{payments_without_order:,}"
)

print(
    f"Reviews without matching order   : "
    f"{reviews_without_order:,}"
)


# ============================================================
# 12. CUSTOMER ID VALIDATION
# ============================================================

section("12. CUSTOMER ID VALIDATION")

customer_id_duplicates = (
    customers["customer_id"]
    .duplicated()
    .sum()
)

print(
    f"Duplicate customer_id : "
    f"{customer_id_duplicates:,}"
)

print(
    f"Unique customer_id    : "
    f"{customers['customer_id'].nunique():,}"
)

print(
    f"Unique customer_unique_id : "
    f"{customers['customer_unique_id'].nunique():,}"
)


# ============================================================
# 13. PRODUCT ID VALIDATION
# ============================================================

section("13. PRODUCT ID VALIDATION")

duplicate_product_ids = (
    products["product_id"]
    .duplicated()
    .sum()
)

print(
    f"Duplicate product_id : "
    f"{duplicate_product_ids:,}"
)

print(
    f"Unique product_id    : "
    f"{products['product_id'].nunique():,}"
)


# ============================================================
# 14. SELLER ID VALIDATION
# ============================================================

section("14. SELLER ID VALIDATION")

duplicate_seller_ids = (
    sellers["seller_id"]
    .duplicated()
    .sum()
)

print(
    f"Duplicate seller_id : "
    f"{duplicate_seller_ids:,}"
)

print(
    f"Unique seller_id    : "
    f"{sellers['seller_id'].nunique():,}"
)


# ============================================================
# 15. REVENUE VALIDATION
# ============================================================

section("15. REVENUE VALIDATION")

product_revenue = (
    order_items["price"].sum()
)

freight_revenue = (
    order_items["freight_value"].sum()
)

print(
    f"Product revenue : "
    f"R$ {product_revenue:,.2f}"
)

print(
    f"Freight value   : "
    f"R$ {freight_revenue:,.2f}"
)


# ============================================================
# 16. FINAL VALIDATION STATUS
# ============================================================

section("16. FINAL VALIDATION STATUS")

checks = {
    "Order item combinations": duplicate_pairs == 0,
    "Negative prices": negative_prices == 0,
    "Negative freight": negative_freight == 0,
    "Negative payments": negative_payments == 0,
    "Invalid review scores": invalid_scores == 0,
    "Customer relationships": orders_without_customer == 0,
    "Order relationships": items_without_order == 0,
    "Product relationships": items_without_product == 0,
    "Seller relationships": items_without_seller == 0,
    "Payment relationships": payments_without_order == 0,
    "Review relationships": reviews_without_order == 0,
    "Duplicate customer IDs": customer_id_duplicates == 0,
    "Duplicate product IDs": duplicate_product_ids == 0,
    "Duplicate seller IDs": duplicate_seller_ids == 0,
}

passed = 0

for check_name, result in checks.items():

    if result:
        print(f"PASS : {check_name}")
        passed += 1
    else:
        print(f"CHECK: {check_name}")


print()
print(
    f"Validation checks passed: "
    f"{passed}/{len(checks)}"
)

if passed == len(checks):

    print(
        "\nFINAL STATUS: PASS"
    )

    print(
        "Processed data passed all "
        "critical validation checks."
    )

else:

    print(
        "\nFINAL STATUS: REVIEW REQUIRED"
    )

    print(
        "One or more critical checks "
        "need attention."
    )

print()
print("=" * 60)
print("RE-VALIDATION COMPLETE")
print("=" * 60)