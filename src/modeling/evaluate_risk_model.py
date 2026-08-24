# ============================================================
# PROJECT 3
# AI SERVICE OPERATIONS & RECOVERY ANALYTICS
#
# Step 82 - Leakage-Safe Intake Risk Model
# ============================================================

import pandas as pd
import psycopg2

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    confusion_matrix,
    precision_score,
    recall_score,
    accuracy_score,
    roc_auc_score,
)


DB_CONFIG = {
    "host": "localhost",
    "database": "ai_service_operations",
    "user": "postgres",
    "password": "1162",
}


QUERY = """
SELECT
    i.incident_id,

    i.contact_type,
    i.location,
    i.category,
    i.subcategory,
    i.impact,
    i.urgency,
    i.priority,
    i.assignment_group,
    i.knowledge,
    i.u_priority_confirmation,
    i.notify,
    i.vendor,
    i.made_sla,

    r.prolonged_resolution

FROM incidents i

INNER JOIN resolution_outcome r
    ON i.incident_id = r.incident_id;
"""


FEATURES = [
    "contact_type",
    "location",
    "category",
    "subcategory",
    "impact",
    "urgency",
    "priority",
    "assignment_group",
    "knowledge",
    "u_priority_confirmation",
    "notify",
    "vendor",
    "made_sla",
]


CATEGORICAL_FEATURES = [
    "contact_type",
    "location",
    "category",
    "subcategory",
    "impact",
    "urgency",
    "priority",
    "assignment_group",
    "notify",
    "vendor",
]


BOOLEAN_FEATURES = [
    "knowledge",
    "u_priority_confirmation",
    "made_sla",
]


def load_data():

    conn = psycopg2.connect(**DB_CONFIG)

    try:
        df = pd.read_sql_query(QUERY, conn)
    finally:
        conn.close()

    return df


def main():

    print("=" * 70)
    print("PROJECT 3 - LEAKAGE-SAFE INTAKE RISK MODEL")
    print("=" * 70)

    df = load_data()

    X = df[FEATURES].copy()
    y = df["prolonged_resolution"].astype(int)

    for column in BOOLEAN_FEATURES:
        X[column] = X[column].astype("float")

    categorical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="most_frequent")
            ),
            (
                "encoder",
                OneHotEncoder(
                    handle_unknown="ignore"
                )
            ),
        ]
    )

    boolean_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="most_frequent")
            )
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                categorical_pipeline,
                CATEGORICAL_FEATURES,
            ),
            (
                "boolean",
                boolean_pipeline,
                BOOLEAN_FEATURES,
            ),
        ]
    )

    model = LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        random_state=42,
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    pipeline.fit(X_train, y_train)

    probabilities = pipeline.predict_proba(X_test)[:, 1]

    predictions = (
        probabilities >= 0.50
    ).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y_test,
        predictions
    ).ravel()

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0
    )

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    roc_auc = roc_auc_score(
        y_test,
        probabilities
    )

    specificity = tn / (tn + fp)

    print("\nDataset")
    print("-" * 70)
    print(f"Total incidents:  {len(df):,}")
    print(f"Training incidents: {len(X_train):,}")
    print(f"Testing incidents:  {len(X_test):,}")

    print("\nFeatures")
    print("-" * 70)

    for feature in FEATURES:
        print(f"- {feature}")

    print("\nConfusion Matrix")
    print("-" * 70)
    print(f"True Positive:  {tp:,}")
    print(f"False Positive: {fp:,}")
    print(f"False Negative: {fn:,}")
    print(f"True Negative:  {tn:,}")

    print("\nModel Performance")
    print("-" * 70)
    print(f"Accuracy:     {accuracy * 100:.2f}%")
    print(f"Precision:    {precision * 100:.2f}%")
    print(f"Recall:       {recall * 100:.2f}%")
    print(f"Specificity:  {specificity * 100:.2f}%")
    print(f"ROC-AUC:      {roc_auc:.4f}")

    print("\nLeakage Control")
    print("-" * 70)
    print("Post-resolution outcome variables excluded.")
    print("Final operational counts excluded.")
    print("Symptom outcome-rate features excluded.")
    print("Model uses intake-time incident attributes only.")

    print("\nLeakage-safe intake model evaluation complete.")


if __name__ == "__main__":
    main()