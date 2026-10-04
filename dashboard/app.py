import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Clinical Impact Equipment Dashboard",
    page_icon="🏥",
    layout="wide"
)


# =========================================================
# ADD SRC FOLDER TO PYTHON PATH
# =========================================================

SRC_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "src"
    )
)

sys.path.append(SRC_PATH)


# =========================================================
# IMPORT PROJECT FUNCTIONS
# =========================================================

from scoring import calculate_clinical_impact

from operational import (
    add_operational_data,
    generate_recommendation
)


# =========================================================
# LOAD DATASET
# =========================================================

DATA_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "data",
    "equipment_district_hospital.csv"
)

df = pd.read_csv(DATA_PATH)


# =========================================================
# CALCULATE CLINICAL IMPACT
# =========================================================

df = calculate_clinical_impact(df)


# =========================================================
# ADD OPERATIONAL SIMULATION DATA
# =========================================================

df = add_operational_data(df)


# =========================================================
# DATA FRESHNESS
# =========================================================

data_generated_time = datetime.now()

# Prototype freshness simulation
data_age_hours = 2

if data_age_hours <= 6:

    freshness_status = "FRESH"

elif data_age_hours <= 24:

    freshness_status = "STALE"

else:

    freshness_status = "VERY STALE"


# =========================================================
# GENERATE RECOMMENDATIONS
# =========================================================

recommendations = df.apply(
    generate_recommendation,
    axis=1,
    result_type="expand"
)

df["recommendation"] = recommendations[0]

df["recommendation_reason"] = recommendations[1]


# =========================================================
# DASHBOARD HEADER
# =========================================================

st.title(
    "🏥 Clinical-Impact-Aware Equipment Downtime Dashboard"
)

st.write(
    "Decision-support dashboard for prioritizing equipment "
    "maintenance based on clinical impact and operational constraints."
)


# =========================================================
# DATA FRESHNESS STATUS
# =========================================================

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


# =========================================================
# SAFE FALLBACK
# =========================================================

if freshness_status != "FRESH":

    st.info(
        "Safe fallback: Use REVIEW REQUIRED and verify "
        "current equipment status, alternatives and capacity "
        "before maintenance action."
    )


# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.header("Filters")


# Department filter

departments = [
    "All"
] + sorted(
    df["department"]
    .dropna()
    .unique()
    .tolist()
)

selected_department = st.sidebar.selectbox(
    "Department",
    departments
)


# Priority filter

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


# High-impact filter

show_high_impact_only = st.sidebar.checkbox(
    "Show High-Impact Equipment Only"
)


# =========================================================
# APPLY FILTERS
# =========================================================

filtered_df = df.copy()


if selected_department != "All":

    filtered_df = filtered_df[
        filtered_df["department"] == selected_department
    ]


if selected_priority != "All":

    filtered_df = filtered_df[
        filtered_df["priority"] == selected_priority
    ]


if show_high_impact_only:

    filtered_df = filtered_df[
        (
            filtered_df["services_disrupted"] == 1
        )
        &
        (
            filtered_df[
                "patients_referred_equipment_down"
            ] > 0
        )
    ]


# =========================================================
# MAIN KPI METRICS
# =========================================================

st.subheader("Operational Overview")

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
            (
                filtered_df["priority"] == "HIGH"
            ).sum()
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


# =========================================================
# MAINTENANCE PRIORITY DISTRIBUTION
# =========================================================

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


st.bar_chart(
    priority_counts
)


# =========================================================
# DEPARTMENT-WISE CLINICAL IMPACT
# =========================================================

st.subheader(
    "Department-wise Clinical Impact"
)


if len(filtered_df) > 0:

    department_impact = (
        filtered_df
        .groupby("department")
        .agg(
            average_clinical_impact=(
                "clinical_impact_score",
                "mean"
            ),
            total_patients_affected=(
                "patients_referred_equipment_down",
                "sum"
            ),
            service_disruptions=(
                "services_disrupted",
                "sum"
            ),
            equipment_count=(
                "id",
                "count"
            )
        )
        .sort_values(
            "average_clinical_impact",
            ascending=False
        )
    )

    st.dataframe(
        department_impact.round(2),
        use_container_width=True
    )

else:

    st.info(
        "No department data available for the selected filters."
    )


# =========================================================
# AVERAGE CLINICAL IMPACT BY DEPARTMENT
# =========================================================

if len(filtered_df) > 0:

    st.subheader(
        "Average Clinical Impact by Department"
    )

    department_chart = (
        department_impact[
            "average_clinical_impact"
        ]
        .sort_values(
            ascending=False
        )
    )

    st.bar_chart(
        department_chart
    )


# =========================================================
# CLINICAL IMPACT RISK DISTRIBUTION
# =========================================================

st.subheader(
    "Clinical Impact Risk Distribution"
)


if len(filtered_df) > 0:

    risk_df = filtered_df.copy()

    risk_df["impact_range"] = pd.cut(
        risk_df["clinical_impact_score"],
        bins=[
            0,
            25,
            50,
            75,
            100
        ],
        labels=[
            "0-25 Low",
            "25-50 Moderate",
            "50-75 High",
            "75-100 Very High"
        ],
        include_lowest=True
    )

    risk_distribution = (
        risk_df["impact_range"]
        .value_counts()
        .reindex(
            [
                "0-25 Low",
                "25-50 Moderate",
                "50-75 High",
                "75-100 Very High"
            ]
        )
        .fillna(0)
    )

    st.bar_chart(
        risk_distribution
    )


    risk_summary = pd.DataFrame({
        "Impact Range": risk_distribution.index,
        "Equipment Count": (
            risk_distribution
            .values
            .astype(int)
        )
    })


    st.dataframe(
        risk_summary,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "No equipment available for risk distribution."
    )


# =========================================================
# DATA QUALITY & RELIABILITY
# =========================================================

st.subheader(
    "Data Quality & Reliability"
)


total_records = len(df)

missing_values = int(
    df.isnull().sum().sum()
)

duplicate_records = int(
    df.duplicated().sum()
)

operational_data_status = "SIMULATED"


if freshness_status == "FRESH":

    reliability_status = "RELIABLE FOR REVIEW"

else:

    reliability_status = "REVIEW REQUIRED"


q1, q2, q3, q4 = st.columns(4)


with q1:

    st.metric(
        "Total Records",
        total_records
    )


with q2:

    st.metric(
        "Missing Values",
        missing_values
    )


with q3:

    st.metric(
        "Duplicate Records",
        duplicate_records
    )


with q4:

    st.metric(
        "Data Freshness",
        freshness_status
    )


st.write(
    "**Operational Data:**",
    operational_data_status
)

st.write(
    "**Recommendation Status:**",
    reliability_status
)


if missing_values > 0:

    st.warning(
        "Missing data detected. Recommendations should "
        "be reviewed before operational action."
    )

elif duplicate_records > 0:

    st.warning(
        "Duplicate records detected. Data quality "
        "should be reviewed."
    )

else:

    st.success(
        "No missing or duplicate records detected "
        "in the current dataset."
    )


st.info(
    "Operational values such as scheduled procedures, "
    "alternative capacity and repair estimates are "
    "simulated prototype values and must be verified "
    "against current operational data before real-world use."
)


# =========================================================
# HIGH-IMPACT EQUIPMENT SUMMARY
# =========================================================

st.subheader(
    "High-Impact Equipment Summary"
)


high_impact_df = filtered_df[
    (
        filtered_df["services_disrupted"] == 1
    )
    &
    (
        filtered_df[
            "patients_referred_equipment_down"
        ] > 0
    )
]


h1, h2, h3, h4 = st.columns(4)


with h1:

    st.metric(
        "High-Impact Equipment",
        len(high_impact_df)
    )


with h2:

    st.metric(
        "Patients Affected",
        int(
            high_impact_df[
                "patients_referred_equipment_down"
            ].sum()
        )
    )


with h3:

    st.metric(
        "Service Disruptions",
        int(
            high_impact_df[
                "services_disrupted"
            ].sum()
        )
    )


with h4:

    st.metric(
        "Currently Non-Functional",
        int(
            (
                high_impact_df[
                    "currently_functional"
                ] == 0
            ).sum()
        )
    )


# =========================================================
# TOP MAINTENANCE PRIORITIES
# =========================================================

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


if len(filtered_df) > 0:

    top_equipment = (
        filtered_df[
            display_columns
        ]
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

else:

    st.info(
        "No equipment matches the selected filters."
    )


# =========================================================
# EXPORT FILTERED EQUIPMENT REPORT
# =========================================================

st.subheader(
    "Export Equipment Report"
)


export_columns = [
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
    "recommendation",
    "recommendation_reason"
]


export_df = filtered_df[
    export_columns
].copy()


csv_data = export_df.to_csv(
    index=False
).encode("utf-8")


st.download_button(
    label="Download Filtered Equipment Report",
    data=csv_data,
    file_name="equipment_maintenance_report.csv",
    mime="text/csv"
)


st.caption(
    "The exported report reflects the currently selected "
    "department, priority and high-impact filters."
)


# =========================================================
# EXECUTIVE OVERVIEW
# =========================================================

st.subheader(
    "Executive Overview"
)


if len(filtered_df) > 0:

    total_equipment = len(
        filtered_df
    )


    high_impact_count = len(
        filtered_df[
            (
                filtered_df[
                    "services_disrupted"
                ] == 1
            )
            &
            (
                filtered_df[
                    "patients_referred_equipment_down"
                ] > 0
            )
        ]
    )


    high_impact_percentage = (
        high_impact_count
        / total_equipment
    ) * 100


    total_patients = int(
        filtered_df[
            "patients_referred_equipment_down"
        ].sum()
    )


    service_disruption_percentage = (
        filtered_df[
            "services_disrupted"
        ].sum()
        / total_equipment
    ) * 100


    average_downtime = (
        filtered_df[
            "downtime_days_last_6m"
        ].mean()
    )


    overview_col1, overview_col2 = st.columns(2)


    with overview_col1:

        st.write(
            "**Equipment Overview**"
        )

        st.write(
            f"Total equipment: **{total_equipment}**"
        )

        st.write(
            f"High-impact equipment: "
            f"**{high_impact_count} "
            f"({high_impact_percentage:.1f}%)**"
        )

        st.write(
            f"Patients affected: "
            f"**{total_patients}**"
        )


    with overview_col2:

        st.write(
            "**Operational Overview**"
        )

        st.write(
            f"Service disruption rate: "
            f"**{service_disruption_percentage:.1f}%**"
        )

        st.write(
            f"Average downtime: "
            f"**{average_downtime:.1f} days**"
        )

        st.write(
            f"Data status: "
            f"**{freshness_status}**"
        )


    st.info(
        "This dashboard is a prototype decision-support tool. "
        "Operational values such as scheduled procedures, "
        "alternative capacity and repair estimates are simulated "
        "and must be verified against current operational data "
        "before real-world maintenance decisions."
    )

else:

    st.info(
        "No data available for the selected filters."
    )


# =========================================================
# EQUIPMENT DRILL-DOWN
# =========================================================

st.subheader(
    "Equipment Drill-Down"
)


equipment_ids = filtered_df[
    "id"
].tolist()


if equipment_ids:

    selected_id = st.selectbox(
        "Select Equipment ID",
        equipment_ids
    )


    equipment = filtered_df[
        filtered_df["id"] == selected_id
    ].iloc[0]


    # =====================================================
    # BASIC EQUIPMENT METRICS
    # =====================================================

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


    # =====================================================
    # CLINICAL IMPACT SCORE BREAKDOWN
    # =====================================================

    st.subheader(
        "Clinical Impact Score Breakdown"
    )


    score_col1, score_col2 = st.columns(2)


    with score_col1:

        downtime_contribution = (
            equipment[
                "downtime_score"
            ] * 0.30
        )


        patient_contribution = (
            equipment[
                "patient_impact_score"
            ] * 0.25
        )


        st.metric(
            "Downtime Contribution",
            f"{downtime_contribution:.1f}"
        )


        st.metric(
            "Patient Impact Contribution",
            f"{patient_contribution:.1f}"
        )


    with score_col2:

        service_contribution = (
            equipment[
                "service_impact_score"
            ] * 0.25
        )


        availability_contribution = (
            equipment[
                "availability_score"
            ] * 0.20
        )


        st.metric(
            "Service Disruption Contribution",
            f"{service_contribution:.1f}"
        )


        st.metric(
            "Availability Contribution",
            f"{availability_contribution:.1f}"
        )


    # =====================================================
    # SCORE CALCULATION
    # =====================================================

    total_score = (
        downtime_contribution
        + patient_contribution
        + service_contribution
        + availability_contribution
    )


    st.write(
        f"**Score Calculation:** "
        f"{downtime_contribution:.1f} + "
        f"{patient_contribution:.1f} + "
        f"{service_contribution:.1f} + "
        f"{availability_contribution:.1f} "
        f"= **{total_score:.1f}**"
    )


    # =====================================================
    # PRIORITY EXPLANATION
    # =====================================================

    if equipment["priority"] == "HIGH":

        st.warning(
            "High priority because the combined clinical "
            "and operational impact is significant."
        )


    elif equipment["priority"] == "MEDIUM":

        st.info(
            "Medium priority because the equipment has "
            "a moderate combined impact."
        )


    else:

        st.success(
            "Low priority because the combined impact "
            "is currently low."
        )


    # =====================================================
    # EQUIPMENT DETAILS
    # =====================================================

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


    # =====================================================
    # MAINTENANCE RECOMMENDATION
    # =====================================================

    st.subheader(
        "Maintenance Recommendation"
    )


    recommendation = equipment[
        "recommendation"
    ]


    if recommendation == "URGENT":

        st.error(
            "URGENT"
        )


    elif recommendation == "HIGH":

        st.warning(
            "HIGH"
        )


    elif recommendation == "MEDIUM":

        st.info(
            "MEDIUM"
        )


    else:

        st.success(
            "LOW"
        )


    st.write(
        "**Reason:**",
        equipment[
            "recommendation_reason"
        ]
    )


    # =====================================================
    # RECOMMENDATION EVIDENCE
    # =====================================================

    st.subheader(
        "Recommendation Evidence"
    )


    evidence_col1, evidence_col2 = st.columns(2)


    with evidence_col1:

        st.write(
            "**Clinical Impact Score:**",
            f"{equipment['clinical_impact_score']:.1f}"
        )


        st.write(
            "**Priority:**",
            equipment["priority"]
        )


        st.write(
            "**Service Disrupted:**",
            "Yes"
            if equipment["services_disrupted"] == 1
            else "No"
        )


        st.write(
            "**Patients Affected:**",
            int(
                equipment[
                    "patients_referred_equipment_down"
                ]
            )
        )


    with evidence_col2:

        st.write(
            "**Scheduled Procedures:**",
            int(
                equipment[
                    "scheduled_procedures_7d"
                ]
            )
        )


        st.write(
            "**Alternative Capacity:**",
            int(
                equipment[
                    "alternative_capacity"
                ]
            )
        )


        st.write(
            "**Alternative Available:**",
            "Yes"
            if equipment[
                "alternative_available"
            ] == 1
            else "No"
        )


        st.write(
            "**Repair Estimate:**",
            f"{equipment['repair_estimate_days']} days"
        )


    # =====================================================
    # DECISION SAFETY STATUS
    # =====================================================

    st.subheader(
        "Decision Safety Status"
    )


    if freshness_status != "FRESH":

        st.error(
            "REVIEW REQUIRED — Data freshness is not "
            "sufficient for direct maintenance action."
        )


    elif recommendation == "URGENT":

        st.warning(
            "ACTION REVIEW — Urgent recommendation requires "
            "verification of current equipment status and alternatives."
        )


    elif recommendation == "HIGH":

        st.warning(
            "PRIORITY REVIEW — Verify operational evidence "
            "before maintenance scheduling."
        )


    else:

        st.success(
            "INFORMATIONAL — Recommendation can be reviewed "
            "using the displayed evidence."
        )


    # =====================================================
    # OPERATIONAL EVIDENCE
    # =====================================================

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
            if equipment[
                "alternative_available"
            ] == 1
            else "No"
        )


else:

    st.info(
        "No equipment matches the selected filters."
    )