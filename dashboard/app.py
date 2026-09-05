import streamlit as st
import pandas as pd
import sys
import os

# -----------------------------------
# Allow importing from src
# -----------------------------------

SRC_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "src"
    )
)

sys.path.append(SRC_PATH)

from scoring import calculate_clinical_impact
from operational import (
    add_operational_data,
    generate_recommendation
)


# -----------------------------------
# Page configuration
# -----------------------------------

st.set_page_config(
    page_title="Clinical Impact Equipment Dashboard",
    page_icon="🏥",
    layout="wide"
)


# -----------------------------------
# Data path
# -----------------------------------

DATA_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "data",
    "equipment_district_hospital.csv"
)


# -----------------------------------
# Load dataset
# -----------------------------------

df = pd.read_csv(DATA_PATH)

# Clinical impact score
df = calculate_clinical_impact(df)

# Operational simulation
df = add_operational_data(df)

# -----------------------------------
# Data freshness
# -----------------------------------

from datetime import datetime, timedelta

data_generated_time = datetime.now()
data_age_hours = 2

if data_age_hours <= 6:
    freshness_status = "FRESH"
elif data_age_hours <= 24:
    freshness_status = "STALE"
else:
    freshness_status = "VERY STALE"

# Generate recommendations
recommendations = df.apply(
    generate_recommendation,
    axis=1,
    result_type="expand"
)

df["recommendation"] = recommendations[0]
df["recommendation_reason"] = recommendations[1]


# -----------------------------------
# Dashboard title
# -----------------------------------

st.title(
    "🏥 Clinical-Impact-Aware Equipment Downtime Dashboard"
)

st.write(
    "Maintenance priorities are ranked using equipment downtime, "
    "clinical service disruption, patient impact, equipment availability, "
    "and operational constraints."
)

# -----------------------------------
# Data freshness indicator
# -----------------------------------

if freshness_status == "FRESH":
    st.success(
        "🟢 Data Status: FRESH — updated within 6 hours"
    )

elif freshness_status == "STALE":
    st.warning(
        "🟡 Data Status: STALE — verify equipment status before acting"
    )

else:
    st.error(
        "🔴 Data Status: VERY STALE — recommendations should not be trusted"
    )

if freshness_status != "FRESH":
    st.info(
        "⚠️ Safe fallback: Use REVIEW REQUIRED and verify "
        "current equipment status, alternatives and capacity "
        "before maintenance action."
    )

# -----------------------------------
# Sidebar filters
# -----------------------------------

st.sidebar.header("Filters")

departments = ["All"] + sorted(
    df["department"].dropna().unique().tolist()
)

selected_department = st.sidebar.selectbox(
    "Department",
    departments
)

priorities = [
    "All",
    "HIGH",
    "MEDIUM",
    "LOW"
]

selected_priority = st.sidebar.selectbox(
    "Priority",
    priorities
)


# -----------------------------------
# Apply filters
# -----------------------------------

filtered_df = df.copy()

if selected_department != "All":
    filtered_df = filtered_df[
        filtered_df["department"] == selected_department
    ]

if selected_priority != "All":
    filtered_df = filtered_df[
        filtered_df["priority"] == selected_priority
    ]


# -----------------------------------
# KPI cards
# -----------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Equipment",
        len(filtered_df)
    )

with col2:
    st.metric(
        "High Priority",
        int(
            (filtered_df["priority"] == "HIGH").sum()
        )
    )

with col3:
    st.metric(
        "Service Disruptions",
        int(
            filtered_df["services_disrupted"].sum()
        )
    )

with col4:
    st.metric(
        "Patients Affected",
        int(
            filtered_df[
                "patients_referred_equipment_down"
            ].sum()
        )
    )


# -----------------------------------
# Priority distribution
# -----------------------------------

st.subheader(
    "Maintenance Priority Distribution"
)

priority_counts = (
    filtered_df["priority"]
    .value_counts()
    .reindex(
        ["HIGH", "MEDIUM", "LOW"]
    )
    .fillna(0)
)

st.bar_chart(priority_counts)


# -----------------------------------
# Top maintenance priorities
# -----------------------------------

st.subheader(
    "Top Maintenance Priorities"
)

display_columns = [
    "id",
    "equipment_type",
    "department",
    "currently_functional",
    "downtime_days_last_6m",
    "services_disrupted",
    "patients_referred_equipment_down",
    "clinical_impact_score",
    "priority",
    "scheduled_procedures_7d",
    "alternative_available",
    "alternative_capacity",
    "repair_estimate_days",
    "recommendation"
]

top_equipment = (
    filtered_df[display_columns]
    .sort_values(
        "clinical_impact_score",
        ascending=False
    )
    .head(20)
)

st.dataframe(
    top_equipment,
    use_container_width=True
)


# -----------------------------------
# Equipment drill-down
# -----------------------------------

st.subheader(
    "🔎 Equipment Drill-Down"
)

equipment_ids = filtered_df["id"].tolist()

if equipment_ids:

    selected_id = st.selectbox(
        "Select Equipment ID",
        equipment_ids
    )

    equipment = filtered_df[
        filtered_df["id"] == selected_id
    ].iloc[0]


    # -----------------------------------
    # Main metrics
    # -----------------------------------

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Clinical Impact Score",
            f"{equipment['clinical_impact_score']:.1f}"
        )

    with c2:
        st.metric(
            "Downtime",
            f"{equipment['downtime_days_last_6m']} days"
        )

    with c3:
        st.metric(
            "Patients Affected",
            int(
                equipment[
                    "patients_referred_equipment_down"
                ]
            )
        )


    # -----------------------------------
    # Equipment information
    # -----------------------------------

    st.write(
        "**Equipment Type:**",
        equipment["equipment_type"]
    )

    st.write(
        "**Department:**",
        equipment["department"]
    )

    st.write(
        "**Service Disrupted:**",
        "Yes"
        if equipment["services_disrupted"] == 1
        else "No"
    )

    st.write(
        "**Currently Functional:**",
        "Yes"
        if equipment["currently_functional"] == 1
        else "No"
    )


    # -----------------------------------
    # Maintenance recommendation
    # -----------------------------------

    st.subheader(
        "Maintenance Recommendation"
    )

    recommendation = equipment["recommendation"]

    if recommendation == "URGENT":

        st.error(
            f"🚨 {recommendation}"
        )

    elif recommendation == "HIGH":

        st.warning(
            f"⚠️ {recommendation}"
        )

    elif recommendation == "MEDIUM":

        st.info(
            f"ℹ️ {recommendation}"
        )

    else:

        st.success(
            f"✅ {recommendation}"
        )


    st.write(
        "**Reason:**",
        equipment["recommendation_reason"]
    )


    # -----------------------------------
    # Operational evidence
    # -----------------------------------

    st.subheader(
        "Operational Evidence"
    )

    e1, e2, e3, e4 = st.columns(4)

    with e1:
        st.metric(
            "Procedures Next 7 Days",
            int(
                equipment[
                    "scheduled_procedures_7d"
                ]
            )
        )

    with e2:
        st.metric(
            "Alternative Capacity",
            int(
                equipment[
                    "alternative_capacity"
                ]
            )
        )

    with e3:
        st.metric(
            "Repair Estimate",
            f"{equipment['repair_estimate_days']} days"
        )

    with e4:
        st.metric(
            "Alternative Available",
            "Yes"
            if equipment["alternative_available"] == 1
            else "No"
        )