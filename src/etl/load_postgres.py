import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from pathlib import Path


# ============================================================
# PROJECT 3
# AI SERVICE OPERATIONS & RECOVERY ANALYTICS
# PostgreSQL Data Loader
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

EVENT_FILE = PROJECT_ROOT / "data" / "processed" / "incident_events_clean.csv"
INCIDENT_FILE = PROJECT_ROOT / "data" / "processed" / "incidents_analytics.csv"

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "ai_service_operations",
    "user": "postgres",
    "password": "1162",
}


def clean_dataframe(df):
    """Standardize missing values."""

    df = df.replace("?", pd.NA)

    return df


def convert_boolean(value):
    """Convert CSV boolean values to Python booleans."""

    if pd.isna(value):
        return None

    if isinstance(value, bool):
        return value

    value = str(value).strip().lower()

    if value in {"true", "1", "yes"}:
        return True

    if value in {"false", "0", "no"}:
        return False

    return None


def prepare_dates(df, columns):
    """
    Convert dates safely.

    The ETL output may already contain ISO timestamps,
    while the raw event data may use day/month/year format.
    """

    for column in columns:

        if column not in df.columns:
            continue

        # First attempt normal parsing.
        parsed = pd.to_datetime(
            df[column],
            errors="coerce"
        )

        # Only attempt day-first parsing for values that
        # could not be parsed normally.
        missing = parsed.isna() & df[column].notna()

        if missing.any():

            parsed_dayfirst = pd.to_datetime(
                df.loc[missing, column],
                dayfirst=True,
                errors="coerce"
            )

            parsed.loc[missing] = parsed_dayfirst

        df[column] = parsed

    return df


def prepare_events(df):
    """Prepare event-level data."""

    df = clean_dataframe(df)

    date_columns = [
        "opened_at",
        "sys_created_at",
        "sys_updated_at",
        "resolved_at",
        "closed_at",
    ]

    df = prepare_dates(df, date_columns)

    boolean_columns = [
        "active",
        "made_sla",
        "knowledge",
        "u_priority_confirmation",
        "reopen_flag",
    ]

    for column in boolean_columns:

        if column in df.columns:
            df[column] = df[column].apply(convert_boolean)

    integer_columns = [
        "reassignment_count",
        "reopen_count",
        "sys_mod_count",
        "modification_count",
    ]

    for column in integer_columns:

        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    if "reassignment_intensity" in df.columns:

        df["reassignment_intensity"] = pd.to_numeric(
            df["reassignment_intensity"],
            errors="coerce"
        )

    # Preserve source order for deterministic event sequencing.
    df["_source_order"] = range(len(df))

    # Chronological order within each incident.
    df = df.sort_values(
        ["number", "sys_updated_at", "_source_order"],
        kind="stable"
    )

    # Generate lifecycle sequence.
    df["event_sequence"] = (
        df.groupby("number", sort=False)
        .cumcount()
        .add(1)
    )

    df = df.drop(columns=["_source_order"])

    return df


def prepare_incidents(df):
    """Prepare incident-level analytical data."""

    df = clean_dataframe(df)

    date_columns = [
        "opened_at",
        "last_updated_at",
        "closed_at",
        "resolution_timestamp",
    ]

    df = prepare_dates(df, date_columns)

    boolean_columns = [
        "active",
        "made_sla",
        "knowledge",
        "u_priority_confirmation",
        "reopen_flag",
    ]

    for column in boolean_columns:

        if column in df.columns:
            df[column] = df[column].apply(convert_boolean)

    integer_columns = [
        "reopen_count",
        "reassignment_count",
        "sys_mod_count",
        "modification_count",
    ]

    for column in integer_columns:

        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    numeric_columns = [
        "resolution_hours",
        "closure_hours",
        "resolution_to_closure_hours",
        "reassignment_intensity",
    ]

    for column in numeric_columns:

        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    return df


def none_if_nan(value):
    """Convert pandas missing values to Python None."""

    if pd.isna(value):
        return None

    return value


def load_database(incidents, events):

    connection = psycopg2.connect(**DB_CONFIG)

    cursor = None

    try:

        connection.autocommit = False

        cursor = connection.cursor()

        print("\nConnected to PostgreSQL.")
        print("Database:", DB_CONFIG["database"])

        # ----------------------------------------------------
        # CLEAR EXISTING DATA
        # ----------------------------------------------------

        print("\nClearing existing analytical tables...")

        cursor.execute(
            "TRUNCATE TABLE incident_events, incidents RESTART IDENTITY;"
        )

        # ----------------------------------------------------
        # INCIDENTS
        # ----------------------------------------------------

        incident_columns = [
            "incident_id",
            "caller_id",
            "opened_by",
            "opened_at",
            "sys_created_at",
            "last_updated_at",
            "resolved_at",
            "closed_at",
            "resolution_timestamp_source",
            "incident_state",
            "active",
            "contact_type",
            "location",
            "category",
            "subcategory",
            "u_symptom",
            "cmdb_ci",
            "impact",
            "urgency",
            "priority",
            "assignment_group",
            "assigned_to",
            "knowledge",
            "u_priority_confirmation",
            "notify",
            "problem_id",
            "rfc",
            "vendor",
            "caused_by",
            "closed_code",
            "resolved_by",
            "reassignment_count",
            "reopen_count",
            "sys_mod_count",
            "made_sla",
            "resolution_hours",
            "closure_hours",
            "resolution_timestamp",
            "resolution_to_closure_hours",
            "reopen_flag",
            "reassignment_intensity",
            "modification_count",
        ]

        incident_values = []

        for _, row in incidents.iterrows():

            values = []

            for column in incident_columns:

                # The incident analytics CSV does NOT contain
                # sys_created_at. The database column is nullable.
                if column == "sys_created_at":
                    values.append(None)

                else:
                    values.append(
                        none_if_nan(row[column])
                    )

            incident_values.append(tuple(values))

        incident_sql = f"""
            INSERT INTO incidents (
                {", ".join(incident_columns)}
            )
            VALUES %s
        """

        print(
            f"\nLoading incidents: "
            f"{len(incident_values):,}"
        )

        execute_values(
            cursor,
            incident_sql,
            incident_values,
            page_size=1000
        )

        print("Incidents loaded successfully.")

        # ----------------------------------------------------
        # EVENTS
        # ----------------------------------------------------

        event_columns = [
            "incident_id",
            "event_sequence",
            "incident_state",
            "active",
            "made_sla",
            "reassignment_count",
            "reopen_count",
            "sys_mod_count",
            "caller_id",
            "opened_by",
            "opened_at",
            "sys_created_by",
            "sys_created_at",
            "sys_updated_by",
            "sys_updated_at",
            "contact_type",
            "location",
            "category",
            "subcategory",
            "u_symptom",
            "cmdb_ci",
            "impact",
            "urgency",
            "priority",
            "assignment_group",
            "assigned_to",
            "knowledge",
            "u_priority_confirmation",
            "notify",
            "problem_id",
            "rfc",
            "vendor",
            "caused_by",
            "closed_code",
            "resolved_by",
            "resolved_at",
            "closed_at",
            "reopen_flag",
            "reassignment_intensity",
            "modification_count",
        ]

        event_values = []

        for _, row in events.iterrows():

            values = []

            for column in event_columns:

                if column == "incident_id":

                    values.append(
                        none_if_nan(row["number"])
                    )

                else:

                    values.append(
                        none_if_nan(row[column])
                    )

            event_values.append(tuple(values))

        event_sql = f"""
            INSERT INTO incident_events (
                {", ".join(event_columns)}
            )
            VALUES %s
        """

        print(
            f"\nLoading incident events: "
            f"{len(event_values):,}"
        )

        execute_values(
            cursor,
            event_sql,
            event_values,
            page_size=2000
        )

        print("Incident events loaded successfully.")

        # ----------------------------------------------------
        # DATABASE VALIDATION
        # ----------------------------------------------------

        cursor.execute(
            "SELECT COUNT(*) FROM incidents;"
        )

        incident_count = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM incident_events;"
        )

        event_count = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(DISTINCT incident_id)
            FROM incident_events;
            """
        )

        event_incident_count = cursor.fetchone()[0]

        # Duplicate incident IDs should be impossible because
        # incident_id is the primary key.
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM incidents
            WHERE incident_id IS NULL;
            """
        )

        null_incident_ids = cursor.fetchone()[0]

        print("\n========== DATABASE VALIDATION ==========")

        print(
            f"Incidents in database: "
            f"{incident_count:,}"
        )

        print(
            f"Events in database: "
            f"{event_count:,}"
        )

        print(
            f"Incidents represented in events: "
            f"{event_incident_count:,}"
        )

        print(
            f"NULL incident IDs: "
            f"{null_incident_ids:,}"
        )

        # ----------------------------------------------------
        # VALIDATION RULES
        # ----------------------------------------------------

        if incident_count != len(incidents):

            raise ValueError(
                "Incident row count does not match source dataset."
            )

        if event_count != len(events):

            raise ValueError(
                "Event row count does not match source dataset."
            )

        if event_incident_count != incident_count:

            raise ValueError(
                "Event incident coverage does not match "
                "incident table."
            )

        if null_incident_ids != 0:

            raise ValueError(
                "NULL incident IDs detected."
            )

        # ----------------------------------------------------
        # COMMIT
        # ----------------------------------------------------

        connection.commit()

        print(
            "\n========== POSTGRES LOAD COMPLETE =========="
        )

        print(
            "Transaction committed successfully."
        )

    except Exception:

        connection.rollback()

        print(
            "\nERROR: Database load failed."
        )

        print(
            "Transaction rolled back. "
            "No partial load was committed."
        )

        raise

    finally:

        if cursor is not None:
            cursor.close()

        connection.close()


def main():

    print("================================================")
    print("PROJECT 3 - POSTGRESQL DATA LOAD")
    print("================================================")

    # --------------------------------------------------------
    # LOAD SOURCE DATA
    # --------------------------------------------------------

    print("\nLoading incident dataset...")

    incidents = pd.read_csv(
        INCIDENT_FILE,
        low_memory=False
    )

    print(
        f"Incident rows: "
        f"{len(incidents):,}"
    )

    print(
        f"Incident columns: "
        f"{len(incidents.columns)}"
    )

    print("\nLoading event dataset...")

    events = pd.read_csv(
        EVENT_FILE,
        low_memory=False
    )

    print(
        f"Event rows: "
        f"{len(events):,}"
    )

    print(
        f"Event columns: "
        f"{len(events.columns)}"
    )

    # --------------------------------------------------------
    # PREPARE DATA
    # --------------------------------------------------------

    print("\nPreparing incident data...")

    incidents = prepare_incidents(
        incidents
    )

    print("Preparing event data...")

    events = prepare_events(
        events
    )

    print("\nPreparation complete.")

    # --------------------------------------------------------
    # LOAD DATABASE
    # --------------------------------------------------------

    incidents["resolved_at"] = incidents["resolution_timestamp"]

    load_database(
        incidents=incidents,
        events=events
    )


if __name__ == "__main__":
    main()

