from .database import get_connection


def get_kpis():
    query = """
    SELECT
        COUNT(*) AS total_incidents,
        COUNT(*) FILTER (
            WHERE prolonged_resolution = TRUE
        ) AS prolonged_incidents
    FROM resolution_outcome;
    """

    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            row = cursor.fetchone()
    finally:
        conn.close()

    total_incidents = int(row[0])
    prolonged_incidents = int(row[1])

    prolonged_rate = (
        prolonged_incidents / total_incidents * 100
        if total_incidents > 0
        else 0
    )

    return {
        "total_incidents": total_incidents,
        "prolonged_incidents": prolonged_incidents,
        "prolonged_rate": prolonged_rate,
    }


def get_risk_overview():
    query = """
    SELECT
        combined_risk_band,
        COUNT(*) AS incident_count,
        COUNT(*) FILTER (
            WHERE prolonged_resolution = TRUE
        ) AS prolonged_incidents
    FROM service_recovery_recommendations
    GROUP BY combined_risk_band
    ORDER BY
        CASE combined_risk_band
            WHEN 'High: Complexity + Symptom' THEN 1
            WHEN 'Elevated: Complexity only' THEN 2
            WHEN 'Elevated: Symptom only' THEN 3
            ELSE 4
        END;
    """

    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
    finally:
        conn.close()

    return rows, columns


def get_priority_incidents(limit=25):
    query = """
    SELECT
        incident_id,
        u_symptom,
        combined_risk_band,
        symptom_smoothed_risk_pct,
        symptom_risk_lift_pct_points,
        complexity_risk_flag,
        primary_recommendation,
        recommended_priority,
        prolonged_resolution
    FROM service_recovery_recommendations
    ORDER BY
        recommended_priority ASC,
        symptom_smoothed_risk_pct DESC,
        symptom_risk_lift_pct_points DESC,
        incident_id
    LIMIT %s;
    """

    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (limit,))
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
    finally:
        conn.close()

    return rows, columns


def get_incident_intelligence(limit=100):
    query = """
    SELECT
        incident_id,
        u_symptom,
        combined_risk_band,
        prolonged_resolution,
        symptom_incident_count,
        symptom_prolonged_incidents,
        symptom_prolonged_rate_pct,
        symptom_smoothed_risk_pct,
        symptom_risk_lift_pct_points,
        complexity_risk_flag,
        primary_recommendation,
        recommendation_reason,
        recommended_priority
    FROM service_recovery_recommendations
    ORDER BY recommended_priority ASC, incident_id
    LIMIT %s;
    """

    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (limit,))
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
    finally:
        conn.close()

    return rows, columns


def get_incident_detail(incident_id):
    query = """
    SELECT
        incident_id,
        u_symptom,
        combined_risk_band,
        prolonged_resolution,
        symptom_incident_count,
        symptom_prolonged_incidents,
        symptom_prolonged_rate_pct,
        symptom_smoothed_risk_pct,
        symptom_risk_lift_pct_points,
        complexity_risk_flag,
        primary_recommendation,
        recommendation_reason,
        recommended_priority
    FROM service_recovery_recommendations
    WHERE incident_id = %s;
    """

    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (incident_id,))
            row = cursor.fetchone()
            columns = [description[0] for description in cursor.description]
    finally:
        conn.close()

    if row is None:
        return None

    return dict(zip(columns, row))

def get_operator_actions(incident_id):
    query = """
    SELECT
        action_id,
        incident_id,
        action_type,
        operator_note,
        created_at
    FROM operator_actions
    WHERE incident_id = %s
    ORDER BY created_at DESC;
    """

    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (incident_id,))
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
    finally:
        conn.close()

    return rows, columns

def search_incident(incident_id):
    query = """
    SELECT
        incident_id,
        u_symptom,
        combined_risk_band,
        prolonged_resolution,
        symptom_incident_count,
        symptom_prolonged_incidents,
        symptom_prolonged_rate_pct,
        symptom_smoothed_risk_pct,
        symptom_risk_lift_pct_points,
        complexity_risk_flag,
        primary_recommendation,
        recommendation_reason,
        recommended_priority
    FROM service_recovery_recommendations
    WHERE UPPER(incident_id) = UPPER(%s);
    """

    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (incident_id.strip(),))
            row = cursor.fetchone()
            columns = [description[0] for description in cursor.description]
    finally:
        conn.close()

    if row is None:
        return None

    return dict(zip(columns, row))

def get_operator_action_summary():
    query = """
    SELECT
        COUNT(*) AS total_actions,
        COUNT(*) FILTER (
            WHERE action_type = 'Escalate'
        ) AS escalation_actions,
        MAX(created_at) AS latest_action_at
    FROM operator_actions;
    """

    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            row = cursor.fetchone()
            columns = [description[0] for description in cursor.description]
    finally:
        conn.close()

    return dict(zip(columns, row))

def get_business_impact_summary():
    query = """
    SELECT
        COUNT(*) AS total_incidents,
        COUNT(*) FILTER (
            WHERE prolonged_resolution = TRUE
        ) AS total_prolonged_incidents,
        COUNT(*) FILTER (
            WHERE combined_risk_band = 'High: Complexity + Symptom'
        ) AS high_risk_incidents,
        COUNT(*) FILTER (
            WHERE combined_risk_band = 'High: Complexity + Symptom'
            AND prolonged_resolution = TRUE
        ) AS high_risk_prolonged_incidents
    FROM service_recovery_recommendations;
    """

    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            row = cursor.fetchone()
            columns = [
                description[0]
                for description in cursor.description
            ]
    finally:
        conn.close()

    summary = dict(zip(columns, row))

    total_prolonged = int(
        summary["total_prolonged_incidents"] or 0
    )

    high_risk_prolonged = int(
        summary["high_risk_prolonged_incidents"] or 0
    )

    summary["high_risk_prolonged_share_pct"] = (
        high_risk_prolonged / total_prolonged * 100
        if total_prolonged > 0
        else 0
    )

    summary["high_risk_prolonged_rate_pct"] = (
        high_risk_prolonged
        / int(summary["high_risk_incidents"])
        * 100
        if int(summary["high_risk_incidents"] or 0) > 0
        else 0
    )

    return summary

def get_management_recommendations():
    rows, columns = get_risk_overview()

    recommendations = []

    for row in rows:
        risk_band = row[0]
        incident_count = int(row[1])
        prolonged_incidents = int(row[2])

        prolonged_rate = (
            prolonged_incidents / incident_count * 100
            if incident_count > 0
            else 0
        )

        if risk_band == "High: Complexity + Symptom":
            recommendation = (
                "Prioritize immediate escalation and senior ownership "
                "for incidents showing both complexity and symptom risk."
            )
            priority = 1

        elif risk_band == "Elevated: Complexity only":
            recommendation = (
                "Review operational complexity, ownership, routing, "
                "and assignment processes for these incidents."
            )
            priority = 2

        elif risk_band == "Elevated: Symptom only":
            recommendation = (
                "Strengthen symptom-specific troubleshooting, "
                "knowledge guidance, and frontline resolution support."
            )
            priority = 3

        else:
            recommendation = (
                "Continue the standard workflow with routine monitoring "
                "and avoid unnecessary escalation."
            )
            priority = 4

        recommendations.append(
            {
                "risk_band": risk_band,
                "incident_count": incident_count,
                "prolonged_incidents": prolonged_incidents,
                "prolonged_rate_pct": prolonged_rate,
                "priority": priority,
                "recommendation": recommendation,
            }
        )

    recommendations.sort(
        key=lambda item: item["priority"]
    )

    return recommendations
