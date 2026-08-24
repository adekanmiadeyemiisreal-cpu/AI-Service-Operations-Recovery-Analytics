from pathlib import Path
import pandas as pd


# ============================================================
# PROJECT 3 — INCIDENT DATA ETL PIPELINE
# AI Service Operations & Recovery Analytics
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

RAW_FILE = BASE_DIR / "data" / "raw" / "incident_event_log.csv"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

EVENT_OUTPUT = PROCESSED_DIR / "incident_events_clean.csv"
INCIDENT_OUTPUT = PROCESSED_DIR / "incidents_analytics.csv"


def load_raw_data():
    print("Loading raw incident event log...")

    df = pd.read_csv(
        RAW_FILE,
        keep_default_na=False
    )

    print(f"Raw rows loaded: {len(df):,}")
    print(f"Raw columns loaded: {len(df.columns)}")

    return df


def standardize_placeholders(df):
    """Convert source-system placeholders into proper missing values."""

    placeholder_columns = [
        "resolved_at",
        "closed_at",
        "problem_id",
        "rfc",
        "vendor",
        "caused_by",
        "cmdb_ci",
        "assigned_to",
        "resolved_by",
    ]

    for column in placeholder_columns:
        if column in df.columns:
            df[column] = df[column].replace(
                ["?", "NULL", "null", ""],
                pd.NA
            )

    return df


def parse_timestamps(df):
    """Convert date/time columns to datetime."""

    timestamp_columns = [
        "opened_at",
        "sys_created_at",
        "sys_updated_at",
        "resolved_at",
        "closed_at",
    ]

    for column in timestamp_columns:
        df[column] = pd.to_datetime(
            df[column],
            dayfirst=True,
            errors="coerce"
        )

    return df


def normalize_incident_states(df):
    """Normalize the anomalous -100 state."""

    df["incident_state"] = df["incident_state"].replace(
        "-100",
        "Unknown"
    )

    return df


def create_event_level_features(df):
    """Create event-level analytical fields."""

    df["reopen_count"] = pd.to_numeric(
        df["reopen_count"],
        errors="coerce"
    )

    df["reassignment_count"] = pd.to_numeric(
        df["reassignment_count"],
        errors="coerce"
    )

    df["sys_mod_count"] = pd.to_numeric(
        df["sys_mod_count"],
        errors="coerce"
    )

    df["reopen_flag"] = (
        df["reopen_count"] > 0
    ).astype(int)

    df["reassignment_intensity"] = (
        df["reassignment_count"]
    )

    df["modification_count"] = (
        df["sys_mod_count"]
    )

    return df


def derive_resolution_timestamp(events):
    """
    Derive one resolution timestamp per incident.

    Priority:
    1. Valid source resolved_at
    2. sys_updated_at from a Resolved event
    3. Missing
    """

    events = events.sort_values(
        ["number", "sys_updated_at"]
    ).copy()

    source_resolution = (
        events.loc[
            events["resolved_at"].notna()
        ]
        .groupby("number")["resolved_at"]
        .min()
    )

    fallback_resolution = (
        events.loc[
            (events["incident_state"] == "Resolved")
            & (events["sys_updated_at"].notna())
        ]
        .groupby("number")["sys_updated_at"]
        .min()
    )

    resolution = source_resolution.combine_first(
        fallback_resolution
    )

    result = pd.DataFrame({
        "number": resolution.index,
        "resolution_timestamp": resolution.values,
    })

    result["resolution_timestamp_source"] = "source_resolved_at"

    fallback_only = (
        result["number"].isin(fallback_resolution.index)
        & ~result["number"].isin(source_resolution.index)
    )

    result.loc[
        fallback_only,
        "resolution_timestamp_source"
    ] = "resolved_event_sys_updated_at"

    return result


def build_incident_table(events):
    """Create one analytical record per unique incident."""

    events = events.sort_values(
        ["number", "sys_updated_at"]
    ).copy()

    first_event = (
        events
        .groupby("number", as_index=False)
        .first()
    )

    last_event = (
        events
        .groupby("number", as_index=False)
        .last()
    )

    # --------------------------------------------------------
    # First known values
    # --------------------------------------------------------

    incident = first_event[
        [
            "number",
            "opened_at",
            "caller_id",
            "opened_by",
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
            "made_sla",
        ]
    ].copy()

    incident = incident.rename(
        columns={
            "number": "incident_id"
        }
    )

    # --------------------------------------------------------
    # Last known operational values
    # --------------------------------------------------------

    last_event_selected = last_event[
        [
            "number",
            "incident_state",
            "active",
            "sys_updated_at",
            "closed_at",
            "reopen_count",
            "reassignment_count",
            "sys_mod_count",
        ]
    ].copy()

    last_event_selected = last_event_selected.rename(
        columns={
            "number": "incident_id",
            "sys_updated_at": "last_updated_at",
        }
    )

    incident = incident.merge(
        last_event_selected,
        on="incident_id",
        how="left"
    )

    # --------------------------------------------------------
    # Resolution timestamp
    # --------------------------------------------------------

    resolution = derive_resolution_timestamp(events)

    resolution = resolution.rename(
        columns={
            "number": "incident_id"
        }
    )

    incident = incident.merge(
        resolution,
        on="incident_id",
        how="left"
    )

    # --------------------------------------------------------
    # Derived duration metrics
    # --------------------------------------------------------

    incident["resolution_hours"] = (
        incident["resolution_timestamp"]
        - incident["opened_at"]
    ).dt.total_seconds() / 3600

    incident["closure_hours"] = (
        incident["closed_at"]
        - incident["opened_at"]
    ).dt.total_seconds() / 3600

    incident["resolution_to_closure_hours"] = (
        incident["closed_at"]
        - incident["resolution_timestamp"]
    ).dt.total_seconds() / 3600

    # --------------------------------------------------------
    # Derived operational metrics
    # --------------------------------------------------------

    incident["reopen_flag"] = (
        incident["reopen_count"] > 0
    ).astype(int)

    incident["reassignment_intensity"] = (
        incident["reassignment_count"]
    )

    incident["modification_count"] = (
        incident["sys_mod_count"]
    )

    return incident


def validate_outputs(events, incidents):
    """Run reproducibility and data-quality checks."""

    print("\n========== VALIDATION ==========")

    print(
        f"Clean event rows: {len(events):,}"
    )

    print(
        f"Unique incidents: "
        f"{incidents['incident_id'].nunique():,}"
    )

    print(
        f"Event duplicates: "
        f"{events.duplicated().sum():,}"
    )

    print(
        f"Incident duplicates: "
        f"{incidents['incident_id'].duplicated().sum():,}"
    )

    print(
        "Missing resolution timestamps: "
        f"{incidents['resolution_timestamp'].isna().sum():,}"
    )

    print(
        "Resolution fallback records: "
        f"{(incidents['resolution_timestamp_source'] == 'resolved_event_sys_updated_at').sum():,}"
    )

    print(
        "Negative resolution durations: "
        f"{(incidents['resolution_hours'] < 0).sum():,}"
    )

    print(
        "Negative closure durations: "
        f"{(incidents['closure_hours'] < 0).sum():,}"
    )

    print(
        "SLA TRUE: "
        f"{(incidents['made_sla'] == True).sum():,}"
    )

    print(
        "SLA FALSE: "
        f"{(incidents['made_sla'] == False).sum():,}"
    )


def main():

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    events = load_raw_data()

    events = standardize_placeholders(events)

    events = parse_timestamps(events)

    events = normalize_incident_states(events)

    events = create_event_level_features(events)

    incidents = build_incident_table(events)

    events.to_csv(
        EVENT_OUTPUT,
        index=False
    )

    incidents.to_csv(
        INCIDENT_OUTPUT,
        index=False
    )

    validate_outputs(
        events,
        incidents
    )

    print("\n========== ETL COMPLETE ==========")

    print(
        f"Event dataset: {EVENT_OUTPUT}"
    )

    print(
        f"Incident dataset: {INCIDENT_OUTPUT}"
    )


if __name__ == "__main__":
    main()