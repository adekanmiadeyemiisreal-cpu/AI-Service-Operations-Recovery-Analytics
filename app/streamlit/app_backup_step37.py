import streamlit as st

from services.analytics import (
    get_kpis,
    get_risk_overview,
    get_priority_incidents,
    get_incident_intelligence,
    get_incident_detail,
    get_operator_actions,
    search_incident,
)

from services.actions import record_operator_action


st.set_page_config(
    page_title="AI Service Operations & Recovery",
    page_icon="🛡️",
    layout="wide",
)

st.title("AI Service Operations & Recovery")
st.subheader("Service Intelligence & Early-Warning Platform")

st.write(
    "Identify high-risk service incidents early and support faster "
    "recovery decisions before incidents become prolonged."
)

st.info(
    "SaaS MVP — connecting the existing AI Service Operations & "
    "Recovery Analytics engine to an interactive application."
)

st.divider()


# ============================================================
# LIVE KPI SUMMARY
# ============================================================

try:
    kpis = get_kpis()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Incidents",
            f"{kpis['total_incidents']:,}"
        )

    with col2:
        st.metric(
            "Prolonged Resolution Rate",
            f"{kpis['prolonged_rate']:.2f}%"
        )

    with col3:
        st.metric(
            "Prolonged Incidents",
            f"{kpis['prolonged_incidents']:,}"
        )

except Exception as error:
    st.error("Unable to load live Project 3 analytics data.")
    st.exception(error)


st.divider()


# ============================================================
# RISK OVERVIEW
# ============================================================

st.header("Risk Overview")

try:
    risk_rows, risk_columns = get_risk_overview()

    risk_data = {
        row[0]: {
            "incidents": int(row[1]),
            "prolonged": int(row[2]),
        }
        for row in risk_rows
    }

    high = risk_data.get(
        "High: Complexity + Symptom",
        {"incidents": 0, "prolonged": 0}
    )

    complexity = risk_data.get(
        "Elevated: Complexity only",
        {"incidents": 0, "prolonged": 0}
    )

    symptom = risk_data.get(
        "Elevated: Symptom only",
        {"incidents": 0, "prolonged": 0}
    )

    standard = risk_data.get(
        "Standard: Neither",
        {"incidents": 0, "prolonged": 0}
    )

    def rate(group):
        if group["incidents"] == 0:
            return 0

        return group["prolonged"] / group["incidents"] * 100

    high_rate = rate(high)
    complexity_rate = rate(complexity)
    symptom_rate = rate(symptom)
    standard_rate = rate(standard)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "High Risk",
            f"{high['incidents']:,}",
            f"{high_rate:.1f}% prolonged"
        )

    with col2:
        st.metric(
            "Complexity Risk",
            f"{complexity['incidents']:,}",
            f"{complexity_rate:.1f}% prolonged"
        )

    with col3:
        st.metric(
            "Symptom Risk",
            f"{symptom['incidents']:,}",
            f"{symptom_rate:.1f}% prolonged"
        )

    with col4:
        st.metric(
            "Standard",
            f"{standard['incidents']:,}",
            f"{standard_rate:.1f}% prolonged"
        )

    st.markdown("### Operational Priority")

    st.write(
        f"**{high['incidents']:,} high-risk incidents produced "
        f"{high['prolonged']:,} prolonged resolutions "
        f"({high_rate:.1f}%).** These incidents combine elevated "
        "operational complexity with elevated symptom risk and "
        "should receive the earliest attention."
    )

except Exception as error:
    st.error("Unable to load risk overview.")
    st.exception(error)


st.divider()


# ============================================================
# PRIORITY INCIDENT QUEUE
# ============================================================

st.header("Priority Incident Queue")

st.write(
    "Incidents are ranked using the existing recovery-priority "
    "logic so operators can investigate the highest-risk cases first."
)

try:
    priority_rows, priority_columns = get_priority_incidents(25)

    if priority_rows:

        priority_records = []

        for row in priority_rows:
            priority_records.append(
                {
                    "Priority": int(row[7]),
                    "Incident": row[0],
                    "Symptom": row[1],
                    "Risk Band": row[2],
                    "Symptom Risk": f"{float(row[3]):.2f}%",
                    "Risk Lift": f"+{float(row[4]):.2f} pp",
                    "Complexity Risk": (
                        "Yes" if row[5] else "No"
                    ),
                    "Recommendation": row[6],
                    "Historical Outcome": (
                        "Prolonged"
                        if row[8]
                        else "Not prolonged"
                    ),
                }
            )

        st.dataframe(
            priority_records,
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            f"Showing the top {len(priority_records)} incidents "
            "from the live service recovery intelligence layer."
        )

    else:
        st.info("No priority incidents found.")

except Exception as error:
    st.error("Unable to load priority incident queue.")
    st.exception(error)


st.divider()


# ============================================================

# INCIDENT INTELLIGENCE
# ============================================================

st.header("Incident Intelligence")

try:

    priority_rows, priority_columns = get_priority_incidents(25)

    priority_incident_ids = [
        row[0]
        for row in priority_rows
    ]

    if priority_incident_ids:

        selected_incident = st.selectbox(
            "Investigate priority incident",
            priority_incident_ids,
            key="priority_incident_selector",
        )

        incident = get_incident_detail(selected_incident)

        if incident:

            st.subheader(
                f"Incident {incident['incident_id']}"
            )

            risk_band = incident["combined_risk_band"]

            if risk_band == "High: Complexity + Symptom":
                st.error(f"Risk Band: {risk_band}")

            elif risk_band.startswith("Elevated"):
                st.warning(f"Risk Band: {risk_band}")

            else:
                st.success(f"Risk Band: {risk_band}")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Symptom",
                    incident["u_symptom"]
                )

            with col2:
                st.metric(
                    "Symptom Risk",
                    f"{float(incident['symptom_smoothed_risk_pct']):.2f}%"
                )

            with col3:
                st.metric(
                    "Symptom Prolonged Rate",
                    f"{float(incident['symptom_prolonged_rate_pct']):.2f}%"
                )

            with col4:
                st.metric(
                    "Complexity Risk",
                    "Yes"
                    if incident["complexity_risk_flag"]
                    else "No"
                )

            st.divider()

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Risk Lift")

                st.metric(
                    "Symptom Risk Lift",
                    f"+{float(incident['symptom_risk_lift_pct_points']):.2f} pp"
                )

            with col2:
                st.markdown("### Recommended Priority")

                st.metric(
                    "Priority",
                    str(incident["recommended_priority"])
                )

            st.divider()

            st.markdown("### Recovery Recommendation")

            st.warning(
                incident["primary_recommendation"]
            )

            st.markdown("### Why this recommendation?")

            st.write(
                incident["recommendation_reason"].replace(
                    "andsymptom",
                    "and symptom"
                )
            )

            st.markdown("### Historical Outcome")

            if incident["prolonged_resolution"]:
                st.error(
                    "This incident resulted in prolonged resolution."
                )
            else:
                st.success(
                    "This incident did not result in prolonged resolution."
                )

    else:
        st.info(
            "No priority incidents are currently available."
        )

except Exception as error:

    st.error(
        "Unable to load incident intelligence."
    )

    st.exception(error)


st.divider()


# ============================================================
# OPERATOR ACTION
# ============================================================

st.header("Operator Action")

st.write(
    "Record the operational decision taken after reviewing "
    "the incident risk and recovery recommendation."
)

try:

    if priority_incident_ids and incident:

        action_type = st.radio(
            "Select operator action",
            [
                "Escalate",
                "Assign for Review",
                "Continue Monitoring",
            ],
            horizontal=True,
            key="operator_action_type",
        )

        operator_note = st.text_area(
            "Operator note",
            placeholder=(
                "Add context about why this action was taken..."
            ),
            key="operator_note",
        )

        if st.button(
            "Save Operator Action",
            type="primary",
            key="save_operator_action",
        ):

            result = record_operator_action(
                incident_id=incident["incident_id"],
                action_type=action_type,
                operator_note=operator_note.strip() or None,
            )

            st.success(
                f"Action saved successfully. "
                f"Action ID: {result['action_id']}"
            )

            st.caption(
                f"Recorded at {result['created_at']}"
            )

    else:

        st.info(
            "Select a priority incident before recording an action."
        )

except Exception as error:

    st.error(
        "Unable to save operator action."
    )

    st.exception(error)



st.divider()


# PRODUCT PURPOSE
# ============================================================

st.markdown("### What this platform does")

st.write(
    """
    The platform analyzes service incidents, identifies operational
    complexity and risk signals, and provides recovery recommendations
    to help support and service operations teams intervene earlier.
    """
)

st.markdown("### Designed for")

st.write(
    "Support Operations • IT Service Desks • Customer Experience Teams "
    "• Service Operations Managers"
)

st.divider()


# ============================================================
# ACTION HISTORY
# ============================================================

st.header("Action History")

try:

    if incident:

        action_rows, action_columns = get_operator_actions(
            incident["incident_id"]
        )

        if action_rows:

            action_records = []

            for row in action_rows:
                action_records.append(
                    {
                        "Action ID": int(row[0]),
                        "Action": row[2],
                        "Operator Note": row[3] or "",
                        "Created At": row[4].strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                    }
                )

            st.dataframe(
                action_records,
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.info(
                "No operator actions have been recorded "
                "for this incident yet."
            )

    else:

        st.info(
            "Select an incident to view action history."
        )

except Exception as error:

    st.error(
        "Unable to load operator action history."
    )

    st.exception(error)



st.divider()


# ============================================================
# INCIDENT SEARCH
# ============================================================

st.header("Incident Search")

st.write(
    "Search for a specific incident ID and retrieve its "
    "current risk intelligence and recovery recommendation."
)

search_value = st.text_input(
    "Enter incident ID",
    placeholder="Example: INC0005074",
    key="incident_search_input",
)

if st.button(
    "Search Incident",
    type="primary",
    key="search_incident_button",
):

    if not search_value.strip():

        st.warning(
            "Please enter an incident ID."
        )

    else:

        try:

            searched_incident = search_incident(
                search_value.strip()
            )

            if searched_incident:

                st.session_state["searched_incident"] = (
                    searched_incident
                )

                st.success(
                    f"Incident {searched_incident['incident_id']} found."
                )

            else:

                st.session_state["searched_incident"] = None

                st.warning(
                    f"No incident found for "
                    f"'{search_value.strip()}'."
                )

        except Exception as error:

            st.error(
                "Unable to search for the incident."
            )

            st.exception(error)


searched_incident = st.session_state.get(
    "searched_incident"
)

if searched_incident:

    st.markdown("### Search Result")

    risk_band = searched_incident["combined_risk_band"]

    if risk_band == "High: Complexity + Symptom":
        st.error(f"Risk Band: {risk_band}")

    elif risk_band.startswith("Elevated"):
        st.warning(f"Risk Band: {risk_band}")

    else:
        st.success(f"Risk Band: {risk_band}")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Incident",
            searched_incident["incident_id"]
        )

    with col2:
        st.metric(
            "Symptom",
            searched_incident["u_symptom"]
        )

    with col3:
        st.metric(
            "Symptom Risk",
            f"{float(searched_incident['symptom_smoothed_risk_pct']):.2f}%"
        )

    with col4:
        st.metric(
            "Priority",
            str(searched_incident["recommended_priority"])
        )

    st.markdown("### Recovery Recommendation")

    st.warning(
        searched_incident["primary_recommendation"]
    )

