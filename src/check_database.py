import psycopg2


# ============================================================
# DATABASE CONNECTION
# ============================================================

conn = psycopg2.connect(
    host="localhost",
    database="businesspulse",
    user="postgres",
    password="BusinessPulse@2026",
    port="5432"
)

cursor = conn.cursor()


# ============================================================
# GET TABLES
# ============================================================

cursor.execute("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    ORDER BY table_name;
""")

tables = [row[0] for row in cursor.fetchall()]


# ============================================================
# DISPLAY TABLE COLUMNS
# ============================================================

print("=" * 70)
print("POSTGRESQL DATABASE STRUCTURE")
print("=" * 70)

for table in tables:

    print()
    print("-" * 70)
    print(f"TABLE: {table}")
    print("-" * 70)

    cursor.execute("""
        SELECT
            column_name,
            data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = %s
        ORDER BY ordinal_position;
    """, (table,))

    columns = cursor.fetchall()

    for column_name, data_type in columns:
        print(f"{column_name:<45} {data_type}")


# ============================================================
# CLOSE CONNECTION
# ============================================================

cursor.close()
conn.close()


print()
print("=" * 70)
print("DATABASE STRUCTURE CHECK COMPLETE")
print("=" * 70)