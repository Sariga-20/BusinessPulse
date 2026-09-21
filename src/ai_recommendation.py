import os

import ollama
import psycopg2
from dotenv import load_dotenv


# ============================================================
# LOAD DATABASE CONFIGURATION
# ============================================================

load_dotenv()


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )


# ============================================================
# GET BUSINESS METRICS FROM POSTGRESQL
# ============================================================

def get_business_metrics():

    conn = get_connection()
    cursor = conn.cursor()

    # ========================================================
    # 1. OVERALL BUSINESS KPIs
    # ========================================================

    cursor.execute("""
        SELECT
            total_orders,
            total_items,
            total_revenue,
            unique_customers
        FROM public.vw_dashboard_kpis;
    """)

    kpi = cursor.fetchone()

    if not kpi:
        raise ValueError("No data returned from vw_dashboard_kpis.")

    total_orders = int(kpi[0])
    total_items = int(kpi[1])
    total_revenue = float(kpi[2])
    unique_customers = int(kpi[3])

    # ========================================================
    # 2. AVERAGE ORDER VALUE
    # ========================================================

    average_order_value = (
        total_revenue / total_orders
        if total_orders > 0
        else 0
    )

    # ========================================================
    # 3. DELIVERY PERFORMANCE
    # ========================================================

    cursor.execute("""
        SELECT
            delivery_status,
            total_orders
        FROM public.vw_delivery_performance;
    """)

    delivery_rows = cursor.fetchall()

    delivery_total = sum(row[1] for row in delivery_rows)

    early_orders = sum(
        row[1]
        for row in delivery_rows
        if row[0] == "Early"
    )

    late_orders = sum(
        row[1]
        for row in delivery_rows
        if row[0] == "Late"
    )

    early_delivery_percentage = (
        early_orders / delivery_total * 100
        if delivery_total > 0
        else 0
    )

    late_delivery_percentage = (
        late_orders / delivery_total * 100
        if delivery_total > 0
        else 0
    )

    # ========================================================
    # 4. CUSTOMER TYPE
    # ========================================================

    cursor.execute("""
        SELECT
            CASE
                WHEN order_count = 1
                    THEN 'One-Time'
                ELSE 'Repeat'
            END AS customer_type,
            COUNT(*) AS customers
        FROM (
            SELECT
                c.customer_unique_id,
                COUNT(DISTINCT o.order_id) AS order_count
            FROM orders o
            JOIN customers c
                ON o.customer_id = c.customer_id
            GROUP BY c.customer_unique_id
        ) customer_orders
        GROUP BY customer_type;
    """)

    customer_rows = cursor.fetchall()

    customer_total = sum(row[1] for row in customer_rows)

    one_time_customers = sum(
        row[1]
        for row in customer_rows
        if row[0] == "One-Time"
    )

    repeat_customers = sum(
        row[1]
        for row in customer_rows
        if row[0] == "Repeat"
    )

    one_time_customer_percentage = (
        one_time_customers / customer_total * 100
        if customer_total > 0
        else 0
    )

    repeat_customer_percentage = (
        repeat_customers / customer_total * 100
        if customer_total > 0
        else 0
    )

    # ========================================================
    # 5. AVERAGE REVIEW SCORE
    # ========================================================

    cursor.execute("""
        SELECT
            SUM(review_score * total_reviews)::numeric
            / NULLIF(SUM(total_reviews), 0)
        FROM public.vw_review_analysis;
    """)

    review_result = cursor.fetchone()[0]

    average_review_score = (
        float(review_result)
        if review_result is not None
        else 0
    )

    # ========================================================
    # 6. MONTHLY REVENUE
    # ========================================================

    cursor.execute("""
        SELECT
            month,
            revenue
        FROM public.vw_monthly_revenue
        WHERE revenue >= 100000
        ORDER BY month DESC
        LIMIT 2;
    """)

    monthly_rows = cursor.fetchall()

    if not monthly_rows:
        latest_month_revenue = 0
        previous_month_revenue = 0
        revenue_growth = 0

    else:
        latest_month_revenue = float(monthly_rows[0][1])

        previous_month_revenue = (
            float(monthly_rows[1][1])
            if len(monthly_rows) > 1
            else 0
        )

        revenue_growth = (
            (
                latest_month_revenue
                - previous_month_revenue
            )
            / previous_month_revenue
            * 100
            if previous_month_revenue > 0
            else 0
        )

    # ========================================================
    # CLOSE DATABASE CONNECTION
    # ========================================================

    cursor.close()
    conn.close()

    # ========================================================
    # RETURN BUSINESS METRICS
    # ========================================================

    return {
        "total_orders": total_orders,
        "total_items": total_items,
        "total_revenue": total_revenue,
        "unique_customers": unique_customers,
        "average_order_value": average_order_value,
        "revenue_growth": revenue_growth,
        "late_delivery_percentage": late_delivery_percentage,
        "early_delivery_percentage": early_delivery_percentage,
        "one_time_customer_percentage": one_time_customer_percentage,
        "repeat_customer_percentage": repeat_customer_percentage,
        "average_review_score": average_review_score,
    }


# ============================================================
# AI RECOMMENDATION ENGINE
# ============================================================

def generate_recommendations(metrics):
    
    prompt = f"""
You are the BusinessPulse AI Business Intelligence Analyst.

Analyze ONLY the verified business metrics provided below.

VERIFIED BUSINESS METRICS
-------------------------

Total Orders: {metrics['total_orders']:,}
Total Items: {metrics['total_items']:,}
Total Revenue: {metrics['total_revenue']:,.2f}
Unique Customers: {metrics['unique_customers']:,}
Average Order Value: {metrics['average_order_value']:,.2f}

Revenue Growth: {metrics['revenue_growth']:.2f}%

Early Delivery: {metrics['early_delivery_percentage']:.2f}%
Late Delivery: {metrics['late_delivery_percentage']:.2f}%

One-Time Customers: {metrics['one_time_customer_percentage']:.2f}%
Repeat Customers: {metrics['repeat_customer_percentage']:.2f}%

Average Review Score: {metrics['average_review_score']:.2f}/5


ANALYSIS RULES
--------------

- Total Revenue and Revenue Growth are different metrics.
- Never describe Total Revenue as a growth rate.
- Revenue Growth of -4.56% means revenue decreased compared
  with the previous qualifying month.
- Do not invent reasons for revenue changes.
- Do not call the review score low, high, good, or poor unless
  the provided data establishes an appropriate benchmark.
- Do not claim that delivery performance caused the review score.
- Do not invent customer behavior beyond the supplied metrics.
- Treat the high one-time customer percentage as a potential
  customer-retention opportunity.
- Treat the late delivery percentage as an operational area
  that could be improved.
- Recommendations must be directly connected to the metrics.
- Do not invent additional statistics.
- Keep the response concise and suitable for an executive dashboard.
- Never introduce a numerical target, percentage target, or improvement
  target that is not explicitly provided in the metrics.
- Do not claim that one metric causes another unless the provided data
  explicitly establishes that relationship.


OUTPUT FORMAT
-------------

Revenue Insight:
Explain the current revenue and revenue-growth situation.

Customer Insight:
Explain the one-time versus repeat customer distribution
and identify the business opportunity supported by these numbers.

Operations Insight:
Explain the early versus late delivery performance and
mention the average review score without assuming a benchmark.

Recommended Actions:
Provide exactly 3 practical actions.

For each action:
- State what the business should do.
- Explain which metric supports the action.

Do not add any other sections.
"""

    response = ollama.chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]

# ============================================================
# SAVE AI RECOMMENDATIONS FOR POWER BI
# ============================================================

def save_ai_output(recommendations):

    output_file = "dashboard/ai_insights.txt"

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(recommendations)

    print(f"\nAI insights saved to: {output_file}")

# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    try:

        print("\n" + "=" * 70)
        print("BUSINESSPULSE AI ENGINE")
        print("=" * 70)

        print("\nConnecting to BusinessPulse PostgreSQL database...")

        metrics = get_business_metrics()

        print("Business metrics retrieved successfully.")

        print("\nRetrieved Metrics:")
        print("-" * 40)
        print(f"Total Orders: {metrics['total_orders']:,}")
        print(f"Total Items: {metrics['total_items']:,}")
        print(f"Total Revenue: {metrics['total_revenue']:,.2f}")
        print(f"Unique Customers: {metrics['unique_customers']:,}")
        print(f"Average Order Value: {metrics['average_order_value']:,.2f}")
        print(f"Revenue Growth: {metrics['revenue_growth']:.2f}%")
        print(f"Late Delivery: {metrics['late_delivery_percentage']:.2f}%")
        print(f"Early Delivery: {metrics['early_delivery_percentage']:.2f}%")
        print(
            f"One-Time Customers: "
            f"{metrics['one_time_customer_percentage']:.2f}%"
        )
        print(
            f"Repeat Customers: "
            f"{metrics['repeat_customer_percentage']:.2f}%"
        )
        print(
            f"Average Review Score: "
            f"{metrics['average_review_score']:.2f}/5"
        )

        print("\nGenerating AI recommendations...")

        recommendations = generate_recommendations(metrics)
        save_ai_output(recommendations)

        print("\n" + "=" * 70)
        print("BUSINESSPULSE AI RECOMMENDATIONS")
        print("=" * 70)

        print(recommendations)

        print("=" * 70)

    except Exception as e:

        print("\n" + "=" * 70)
        print("ERROR")
        print("=" * 70)

        print(f"\n{type(e).__name__}: {e}")

        print("\nPlease check the error message above.")