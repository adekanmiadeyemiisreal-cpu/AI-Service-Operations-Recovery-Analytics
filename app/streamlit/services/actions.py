from .database import get_connection


VALID_ACTIONS = {
    "Escalate",
    "Assign for Review",
    "Continue Monitoring",
}


def record_operator_action(
    incident_id,
    action_type,
    operator_note=None,
):
    if action_type not in VALID_ACTIONS:
        raise ValueError(
            f"Invalid operator action: {action_type}"
        )

    query = """
        INSERT INTO operator_actions (
            incident_id,
            action_type,
            operator_note
        )
        VALUES (%s, %s, %s)
        RETURNING action_id, created_at;
    """

    conn = get_connection()

    try:
        with conn.cursor() as cursor:

            cursor.execute(
                query,
                (
                    incident_id,
                    action_type,
                    operator_note,
                ),
            )

            result = cursor.fetchone()

        conn.commit()

        return {
            "action_id": result[0],
            "created_at": result[1],
        }

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
