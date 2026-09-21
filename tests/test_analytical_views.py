import psycopg2


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="businesspulse",
        user="postgres",
        password="BusinessPulse@2026",
        port="5432"
    )


# --------------------------------------------------
# TEST 1: CHECK REQUIRED VIEWS EXIST
# --------------------------------------------------

def test_required_views_exist():

    required_views = [
        "vw_dashboard_kpis",
        "vw_monthly_revenue",
        "vw_monthly_orders",
        "vw_order_status",
        "vw_payment_methods",
        "vw_customer_type",
        "vw_customer_value",
        "vw_category_performance",
        "vw_delivery_performance",
        "vw_review_analysis",
        "vw_seller_performance",
        "vw_state_performance",
        "vw_top_products"
    ]

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT table_name
        FROM information_schema.views
        WHERE table_schema = 'public';
    """)

    existing_views = {row[0] for row in cur.fetchall()}

    cur.close()
    conn.close()

    missing_views = [
        view for view in required_views
        if view not in existing_views
    ]

    assert not missing_views, (
        f"Missing analytical views: {missing_views}"
    )


# --------------------------------------------------
# TEST 2: DASHBOARD KPI VIEW
# --------------------------------------------------

def test_dashboard_kpis():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            total_orders,
            total_items,
            total_revenue,
            average_order_value,
            unique_customers
        FROM vw_dashboard_kpis;
    """)

    result = cur.fetchone()

    cur.close()
    conn.close()

    assert result is not None, "Dashboard KPI view returned no data."

    total_orders = result[0]
    total_items = result[1]
    total_revenue = result[2]
    average_order_value = result[3]
    unique_customers = result[4]

    assert total_orders > 0, "Total orders should be greater than zero."
    assert total_items > 0, "Total items should be greater than zero."
    assert total_revenue > 0, "Total revenue should be greater than zero."
    assert average_order_value > 0, "Average order value should be greater than zero."
    assert unique_customers > 0, "Unique customers should be greater than zero."


# --------------------------------------------------
# TEST 3: MONTHLY REVENUE
# --------------------------------------------------

def test_monthly_revenue():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*)
        FROM vw_monthly_revenue;
    """)

    row_count = cur.fetchone()[0]

    cur.close()
    conn.close()

    assert row_count > 0, "Monthly revenue view contains no data."


# --------------------------------------------------
# TEST 4: CATEGORY PERFORMANCE
# --------------------------------------------------

def test_category_performance():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*)
        FROM vw_category_performance;
    """)

    row_count = cur.fetchone()[0]

    cur.close()
    conn.close()

    assert row_count > 0, "Category performance view contains no data."


# --------------------------------------------------
# TEST 5: TOP PRODUCTS
# --------------------------------------------------

def test_top_products():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*)
        FROM vw_top_products;
    """)

    row_count = cur.fetchone()[0]

    cur.close()
    conn.close()

    assert row_count > 0, "Top products view contains no data."


# --------------------------------------------------
# TEST 6: CUSTOMER TYPE
# --------------------------------------------------

def test_customer_type():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*)
        FROM vw_customer_type;
    """)

    row_count = cur.fetchone()[0]

    cur.close()
    conn.close()

    assert row_count > 0, "Customer type view contains no data."


# --------------------------------------------------
# TEST 7: DELIVERY PERFORMANCE
# --------------------------------------------------

def test_delivery_performance():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*)
        FROM vw_delivery_performance;
    """)

    row_count = cur.fetchone()[0]

    cur.close()
    conn.close()

    assert row_count > 0, "Delivery performance view contains no data."


# --------------------------------------------------
# TEST 8: SELLER PERFORMANCE
# --------------------------------------------------

def test_seller_performance():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*)
        FROM vw_seller_performance;
    """)

    row_count = cur.fetchone()[0]

    cur.close()
    conn.close()

    assert row_count > 0, "Seller performance view contains no data."


# --------------------------------------------------
# TEST 9: REVIEW ANALYSIS
# --------------------------------------------------

def test_review_analysis():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*)
        FROM vw_review_analysis;
    """)

    row_count = cur.fetchone()[0]

    cur.close()
    conn.close()

    assert row_count > 0, "Review analysis view contains no data."