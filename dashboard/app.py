import streamlit as st
import pandas as pd
import psycopg2
import altair as alt


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="BusinessPulse Dashboard",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

@st.cache_resource
def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="businesspulse",
        user="postgres",
        password="BusinessPulse@2026",
        port="5432"
    )


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data(query):
    conn = get_connection()
    return pd.read_sql_query(query, conn)


# ============================================================
# DASHBOARD HEADER
# ============================================================

st.title("📊 BusinessPulse")
st.subheader("E-Commerce Business Performance Dashboard")

st.markdown("---")


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_orders = load_data("""
    SELECT COUNT(DISTINCT order_id) AS value
    FROM order_items_with_sellers;
""").iloc[0]["value"]


total_items = load_data("""
    SELECT COUNT(order_item_id) AS value
    FROM order_items_with_sellers;
""").iloc[0]["value"]


total_revenue = load_data("""
    SELECT SUM(price) AS value
    FROM order_items_with_sellers;
""").iloc[0]["value"]


average_order_value = load_data("""
    SELECT ROUND(
        SUM(price) / COUNT(DISTINCT order_id),
        2
    ) AS value
    FROM order_items_with_sellers;
""").iloc[0]["value"]


total_customers = load_data("""
    SELECT COUNT(DISTINCT c.customer_unique_id) AS value
    FROM orders o
    JOIN customers c
        ON o.customer_id = c.customer_id;
""").iloc[0]["value"]


# ============================================================
# KPI CARDS
# ============================================================

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Total Orders",
    f"{total_orders:,}"
)

col2.metric(
    "Items Sold",
    f"{total_items:,}"
)

col3.metric(
    "Total Revenue",
    f"R$ {total_revenue:,.2f}"
)

col4.metric(
    "Average Order Value",
    f"R$ {average_order_value:,.2f}"
)

col5.metric(
    "Unique Customers",
    f"{total_customers:,}"
)


st.markdown("---")


# ============================================================
# REVENUE TREND
# ============================================================

st.header("📈 Revenue Trend")

revenue_trend = load_data("""
    WITH monthly_revenue AS (
        SELECT
            DATE_TRUNC(
                'month',
                o.order_purchase_timestamp
            ) AS month,

            ROUND(
                SUM(oi.price)::numeric,
                2
            ) AS monthly_revenue

        FROM orders o

        JOIN order_items oi
            ON o.order_id = oi.order_id

        GROUP BY
            DATE_TRUNC(
                'month',
                o.order_purchase_timestamp
            )
    ),

    latest_month AS (
        SELECT
            MAX(month) AS max_month
        FROM monthly_revenue
    )

    SELECT
        mr.month,
        mr.monthly_revenue

    FROM monthly_revenue mr

    CROSS JOIN latest_month lm

    WHERE mr.month < lm.max_month

    ORDER BY mr.month;
""")


revenue_trend["month"] = pd.to_datetime(
    revenue_trend["month"]
)


revenue_chart = (
    alt.Chart(revenue_trend)

    .mark_line(
        point=True
    )

    .encode(

        x=alt.X(
            "month:T",
            title="Month",
            axis=alt.Axis(
                format="%b %Y",
                labelAngle=-45
            )
        ),

        y=alt.Y(
            "monthly_revenue:Q",
            title="Revenue (R$)",
            axis=alt.Axis(
                format=",.0f"
            )
        ),

        tooltip=[
            alt.Tooltip(
                "month:T",
                title="Month",
                format="%B %Y"
            ),

            alt.Tooltip(
                "monthly_revenue:Q",
                title="Revenue",
                format=",.2f"
            )
        ]
    )

    .properties(
        height=350
    )
)


st.altair_chart(
    revenue_chart,
    use_container_width=True
)


# ============================================================
# MONTHLY ORDER TREND
# ============================================================

st.header("📦 Monthly Order Trend")

monthly_orders = load_data("""
    WITH monthly_orders AS (
        SELECT
            DATE_TRUNC(
                'month',
                order_purchase_timestamp
            ) AS month,

            COUNT(DISTINCT order_id) AS total_orders

        FROM orders

        GROUP BY
            DATE_TRUNC(
                'month',
                order_purchase_timestamp
            )
    ),

    latest_month AS (
        SELECT
            MAX(month) AS max_month
        FROM monthly_orders
    )

    SELECT
        mo.month,
        mo.total_orders

    FROM monthly_orders mo

    CROSS JOIN latest_month lm

    WHERE mo.month < lm.max_month

    ORDER BY mo.month;
""")


monthly_orders["month"] = pd.to_datetime(
    monthly_orders["month"]
)


orders_chart = (
    alt.Chart(monthly_orders)

    .mark_line(
        point=True
    )

    .encode(

        x=alt.X(
            "month:T",
            title="Month",
            axis=alt.Axis(
                format="%b %Y",
                labelAngle=-45
            )
        ),

        y=alt.Y(
            "total_orders:Q",
            title="Number of Orders",
            axis=alt.Axis(
                format=",.0f"
            )
        ),

        tooltip=[
            alt.Tooltip(
                "month:T",
                title="Month",
                format="%B %Y"
            ),

            alt.Tooltip(
                "total_orders:Q",
                title="Orders",
                format=","
            )
        ]
    )

    .properties(
        height=350
    )
)


st.altair_chart(
    orders_chart,
    use_container_width=True
)


st.markdown("---")


# ============================================================
# CATEGORY PERFORMANCE
# ============================================================

st.header("📦 Category Performance")

category_data = load_data("""
    SELECT
        COALESCE(
            p.product_category_name,
            'Unknown'
        ) AS product_category,

        COUNT(DISTINCT oi.order_id) AS total_orders,

        COUNT(oi.order_item_id) AS items_sold,

        ROUND(
            SUM(oi.price)::numeric,
            2
        ) AS total_revenue

    FROM order_items oi

    JOIN products p
        ON oi.product_id = p.product_id

    GROUP BY
        COALESCE(
            p.product_category_name,
            'Unknown'
        )

    ORDER BY total_revenue DESC;
""")


category_display = category_data.copy()

category_display["total_revenue"] = (
    category_display["total_revenue"]
    .map(lambda x: f"R$ {x:,.2f}")
)


st.dataframe(
    category_display,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# CATEGORY REVENUE CHART
# ============================================================

st.subheader("💰 Revenue by Category")

top_categories = category_data.head(10).copy()

category_chart = (
    alt.Chart(top_categories)

    .mark_bar()

    .encode(

        x=alt.X(
            "total_revenue:Q",
            title="Revenue (R$)",
            axis=alt.Axis(
                format=",.0f"
            )
        ),

        y=alt.Y(
            "product_category:N",
            title=None,
            sort="-x"
        ),

        tooltip=[
            alt.Tooltip(
                "product_category:N",
                title="Category"
            ),

            alt.Tooltip(
                "total_revenue:Q",
                title="Revenue",
                format=",.2f"
            ),

            alt.Tooltip(
                "items_sold:Q",
                title="Items Sold",
                format=","
            )
        ]
    )

    .properties(
        height=400
    )
)


st.altair_chart(
    category_chart,
    use_container_width=True
)


# ============================================================
# TOP PRODUCTS
# ============================================================

st.header("🏆 Top Products")

top_products = load_data("""
    SELECT
        oi.product_id,

        COALESCE(
            p.product_category_name,
            'Unknown'
        ) AS product_category,

        COUNT(
            oi.order_item_id
        ) AS items_sold,

        ROUND(
            SUM(oi.price)::numeric,
            2
        ) AS total_revenue

    FROM order_items oi

    JOIN products p
        ON oi.product_id = p.product_id

    GROUP BY
        oi.product_id,
        p.product_category_name

    ORDER BY total_revenue DESC

    LIMIT 10;
""")


top_products_display = top_products.copy()

top_products_display["total_revenue"] = (
    top_products_display["total_revenue"]
    .map(lambda x: f"R$ {x:,.2f}")
)


st.dataframe(
    top_products_display,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# PAYMENT ANALYSIS
# ============================================================

st.header("💳 Payment Analysis")

payment_data = load_data("""
    SELECT
        payment_type,

        COUNT(DISTINCT order_id) AS total_orders,

        ROUND(
            SUM(payment_value)::numeric,
            2
        ) AS total_payment_value

    FROM order_payments

    GROUP BY payment_type

    ORDER BY total_payment_value DESC;
""")


payment_data["percentage"] = (
    payment_data["total_orders"]
    / payment_data["total_orders"].sum()
    * 100
)


payment_data["label"] = (
    payment_data["total_orders"]
    .map(lambda x: f"{x:,}")
    + " ("
    + payment_data["percentage"]
    .map(lambda x: f"{x:.1f}%")
    + ")"
)


payment_chart = (
    alt.Chart(payment_data)

    .mark_bar()

    .encode(

        x=alt.X(
            "total_orders:Q",
            title="Number of Orders",
            axis=alt.Axis(
                format=",.0f"
            )
        ),

        y=alt.Y(
            "payment_type:N",
            title=None,
            sort="-x"
        ),

        tooltip=[
            alt.Tooltip(
                "payment_type:N",
                title="Payment Type"
            ),

            alt.Tooltip(
                "total_orders:Q",
                title="Orders",
                format=","
            ),

            alt.Tooltip(
                "total_payment_value:Q",
                title="Payment Value",
                format=",.2f"
            ),

            alt.Tooltip(
                "percentage:Q",
                title="Percentage",
                format=".1f"
            )
        ]
    )

    .properties(
        height=300
    )
)


payment_labels = (
    alt.Chart(payment_data)

    .mark_text(
        align="left",
        dx=5
    )

    .encode(

        x="total_orders:Q",

        y=alt.Y(
            "payment_type:N",
            sort="-x"
        ),

        text="label:N"
    )
)


st.altair_chart(
    payment_chart + payment_labels,
    use_container_width=True
)


# ============================================================
# CUSTOMER ANALYSIS
# ============================================================

st.header("👥 Customer Analysis")

customer_type = load_data("""
    WITH customer_orders AS (

        SELECT
            c.customer_unique_id,

            COUNT(
                DISTINCT o.order_id
            ) AS order_count

        FROM customers c

        JOIN orders o
            ON c.customer_id = o.customer_id

        GROUP BY
            c.customer_unique_id
    )

    SELECT

        CASE
            WHEN order_count = 1
                THEN 'One-Time Customer'

            ELSE 'Repeat Customer'

        END AS customer_type,

        COUNT(*) AS total_customers

    FROM customer_orders

    GROUP BY customer_type

    ORDER BY total_customers DESC;
""")


customer_type["percentage"] = (
    customer_type["total_customers"]
    / customer_type["total_customers"].sum()
    * 100
)


customer_type["label"] = (
    customer_type["total_customers"]
    .map(lambda x: f"{x:,}")
    + " ("
    + customer_type["percentage"]
    .map(lambda x: f"{x:.1f}%")
    + ")"
)


customer_chart = (
    alt.Chart(customer_type)

    .mark_bar()

    .encode(

        x=alt.X(
            "total_customers:Q",
            title="Number of Customers",
            axis=alt.Axis(
                format=",.0f"
            )
        ),

        y=alt.Y(
            "customer_type:N",
            title=None,
            sort="-x"
        ),

        tooltip=[
            alt.Tooltip(
                "customer_type:N",
                title="Customer Type"
            ),

            alt.Tooltip(
                "total_customers:Q",
                title="Customers",
                format=","
            ),

            alt.Tooltip(
                "percentage:Q",
                title="Percentage",
                format=".1f"
            )
        ]
    )

    .properties(
        height=250
    )
)


customer_labels = (
    alt.Chart(customer_type)

    .mark_text(
        align="left",
        dx=5
    )

    .encode(

        x="total_customers:Q",

        y=alt.Y(
            "customer_type:N",
            sort="-x"
        ),

        text="label:N"
    )
)


st.altair_chart(
    customer_chart + customer_labels,
    use_container_width=True
)


# ============================================================
# GEOGRAPHIC ANALYSIS
# ============================================================

st.header("🗺️ Geographic Analysis")

state_data = load_data("""
    SELECT
        c.customer_state,

        COUNT(DISTINCT o.order_id) AS total_orders,

        COUNT(
            DISTINCT c.customer_unique_id
        ) AS unique_customers

    FROM customers c

    JOIN orders o
        ON c.customer_id = o.customer_id

    GROUP BY
        c.customer_state

    ORDER BY total_orders DESC;
""")


top_states = state_data.head(10).copy()


state_chart = (
    alt.Chart(top_states)

    .mark_bar()

    .encode(

        x=alt.X(
            "total_orders:Q",
            title="Number of Orders",
            axis=alt.Axis(
                format=",.0f"
            )
        ),

        y=alt.Y(
            "customer_state:N",
            title="State",
            sort="-x"
        ),

        tooltip=[
            alt.Tooltip(
                "customer_state:N",
                title="State"
            ),

            alt.Tooltip(
                "total_orders:Q",
                title="Orders",
                format=","
            ),

            alt.Tooltip(
                "unique_customers:Q",
                title="Customers",
                format=","
            )
        ]
    )

    .properties(
        height=400
    )
)


st.altair_chart(
    state_chart,
    use_container_width=True
)


# ============================================================
# REVIEW SCORE ANALYSIS
# ============================================================

st.header("⭐ Review Score Analysis")

review_data = load_data("""
    SELECT
        review_score,

        COUNT(*) AS total_reviews

    FROM order_reviews

    WHERE review_score IS NOT NULL

    GROUP BY review_score

    ORDER BY review_score;
""")


review_data["percentage"] = (
    review_data["total_reviews"]
    / review_data["total_reviews"].sum()
    * 100
)


review_chart = (
    alt.Chart(review_data)

    .mark_bar()

    .encode(

        x=alt.X(
            "review_score:O",
            title="Review Score"
        ),

        y=alt.Y(
            "total_reviews:Q",
            title="Number of Reviews",
            axis=alt.Axis(
                format=",.0f"
            )
        ),

        tooltip=[
            alt.Tooltip(
                "review_score:O",
                title="Score"
            ),

            alt.Tooltip(
                "total_reviews:Q",
                title="Reviews",
                format=","
            ),

            alt.Tooltip(
                "percentage:Q",
                title="Percentage",
                format=".1f"
            )
        ]
    )

    .properties(
        height=350
    )
)


st.altair_chart(
    review_chart,
    use_container_width=True
)


# Average review score

average_review = load_data("""
    SELECT
        ROUND(
            AVG(review_score)::numeric,
            2
        ) AS value

    FROM order_reviews

    WHERE review_score IS NOT NULL;
""").iloc[0]["value"]


st.metric(
    "Average Review Score",
    f"{average_review:.2f} / 5"
)


# ============================================================
# SELLER PERFORMANCE
# ============================================================

st.header("🏪 Seller Performance")

seller_data = load_data("""
    SELECT
        oi.seller_id,

        COUNT(
            oi.order_item_id
        ) AS items_sold,

        COUNT(
            DISTINCT oi.order_id
        ) AS total_orders,

        ROUND(
            SUM(oi.price)::numeric,
            2
        ) AS total_revenue

    FROM order_items oi

    JOIN sellers s
        ON oi.seller_id = s.seller_id

    GROUP BY
        oi.seller_id

    ORDER BY total_revenue DESC

    LIMIT 10;
""")


seller_display = seller_data.copy()

seller_display["total_revenue"] = (
    seller_display["total_revenue"]
    .map(lambda x: f"R$ {x:,.2f}")
)


st.dataframe(
    seller_display,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# DELIVERY PERFORMANCE
# ============================================================

st.header("🚚 Delivery Performance")

delivery_data = load_data("""
    SELECT

        CASE

            WHEN
                order_delivered_customer_date
                <= order_estimated_delivery_date

            THEN 'Early'

            ELSE 'Late'

        END AS delivery_status,

        COUNT(*) AS total_orders

    FROM orders

    WHERE
        order_delivered_customer_date IS NOT NULL

        AND order_estimated_delivery_date IS NOT NULL

    GROUP BY delivery_status

    ORDER BY total_orders DESC;
""")


delivery_data["percentage"] = (
    delivery_data["total_orders"]
    / delivery_data["total_orders"].sum()
    * 100
)


delivery_data["label"] = (
    delivery_data["total_orders"]
    .map(lambda x: f"{x:,}")
    + " ("
    + delivery_data["percentage"]
    .map(lambda x: f"{x:.1f}%")
    + ")"
)


delivery_chart = (
    alt.Chart(delivery_data)

    .mark_bar()

    .encode(

        x=alt.X(
            "total_orders:Q",
            title="Number of Orders",
            axis=alt.Axis(
                format=",.0f"
            )
        ),

        y=alt.Y(
            "delivery_status:N",
            title=None,
            sort="-x"
        ),

        tooltip=[
            alt.Tooltip(
                "delivery_status:N",
                title="Delivery Status"
            ),

            alt.Tooltip(
                "total_orders:Q",
                title="Orders",
                format=","
            ),

            alt.Tooltip(
                "percentage:Q",
                title="Percentage",
                format=".1f"
            )
        ]
    )

    .properties(
        height=250
    )
)


delivery_labels = (
    alt.Chart(delivery_data)

    .mark_text(
        align="left",
        dx=5
    )

    .encode(

        x="total_orders:Q",

        y=alt.Y(
            "delivery_status:N",
            sort="-x"
        ),

        text="label:N"
    )
)


st.altair_chart(
    delivery_chart + delivery_labels,
    use_container_width=True
)


# ============================================================
# KEY BUSINESS INSIGHTS
# ============================================================

st.header("📋 Key Business Insights")

one_time_customers = int(
    customer_type.loc[
        customer_type["customer_type"] == "One-Time Customer",
        "total_customers"
    ].iloc[0]
)


repeat_customers = int(
    customer_type.loc[
        customer_type["customer_type"] == "Repeat Customer",
        "total_customers"
    ].iloc[0]
)


one_time_percentage = (
    one_time_customers
    / (one_time_customers + repeat_customers)
    * 100
)


repeat_percentage = (
    repeat_customers
    / (one_time_customers + repeat_customers)
    * 100
)


early_percentage = float(
    delivery_data.loc[
        delivery_data["delivery_status"] == "Early",
        "percentage"
    ].iloc[0]
)


late_percentage = float(
    delivery_data.loc[
        delivery_data["delivery_status"] == "Late",
        "percentage"
    ].iloc[0]
)


top_category = category_data.iloc[0]["product_category"]


top_category_revenue = category_data.iloc[0]["total_revenue"]


top_payment = payment_data.iloc[0]["payment_type"]


top_state = state_data.iloc[0]["customer_state"]


top_seller = seller_data.iloc[0]["seller_id"]


insight_col1, insight_col2 = st.columns(2)


with insight_col1:

    st.info(
        f"""
        **👥 Customer Retention**

        {one_time_percentage:.1f}% of customers are one-time customers,
        while {repeat_percentage:.1f}% are repeat customers.

        This indicates a significant opportunity to improve customer
        retention and encourage repeat purchases.
        """
    )


    st.info(
        f"""
        **🚚 Delivery Performance**

        {early_percentage:.1f}% of completed orders were delivered
        on or before the estimated delivery date.

        Late deliveries represented {late_percentage:.1f}% of completed
        orders.
        """
    )


    st.info(
        f"""
        **📦 Leading Category**

        **{top_category}** generated the highest category revenue,
        with approximately **R$ {top_category_revenue:,.2f}**.
        """
    )


with insight_col2:

    st.info(
        f"""
        **💳 Payment Preference**

        **{top_payment}** is the leading payment method based on
        the number of orders recorded in the dataset.
        """
    )


    st.info(
        f"""
        **🗺️ Leading Customer State**

        **{top_state}** generated the highest number of orders
        among the Brazilian states represented in the dataset.
        """
    )


    st.info(
        f"""
        **🏪 Seller Performance**

        Seller **{top_seller}** ranks highest by revenue among
        the sellers included in the analysis.
        """
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "BusinessPulse | E-Commerce Business Intelligence Dashboard"
)

st.caption(
    "Built with PostgreSQL • Python • Pandas • Streamlit • Altair"
)