import pandas as pd
import psycopg2


DB_CONFIG = {
    "host": "localhost",
    "database": "ai_service_operations",
    "user": "postgres",
    "password": "1162",
}


QUERY = """
SELECT
    f.incident_id,
    f.complexity_risk_flag,
    f.prolonged_resolution,

    s.symptom_incident_count,
    s.symptom_prolonged_incidents,
    s.symptom_prolonged_rate_pct,
    s.symptom_smoothed_risk_pct,
    s.symptom_risk_lift_pct_points,

    c.operational_complexity_score,
    c.reassignment_count,
    c.reopen_count,
    c.modification_count

FROM incident_risk_features f

INNER JOIN incident_symptom_features s
    ON f.incident_id = s.incident_id

INNER JOIN incident_complexity c
    ON f.incident_id = c.incident_id;
"""


def load_modeling_data():
    conn = psycopg2.connect(**DB_CONFIG)

    try:
        df = pd.read_sql_query(QUERY, conn)
    finally:
        conn.close()

    return df


if __name__ == "__main__":

    df = load_modeling_data()

    print("=" * 60)
    print("PROJECT 3 - MODELING DATASET")
    print("=" * 60)

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    print("\nColumns:")
    for column in df.columns:
        print(f"- {column}")

    print("\nTarget distribution:")
    print(df["prolonged_resolution"].value_counts(dropna=False))

    print("\nMissing values:")
    print(df.isna().sum())

    print("\nModeling dataset loaded successfully.")
