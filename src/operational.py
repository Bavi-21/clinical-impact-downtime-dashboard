import pandas as pd
import numpy as np


def add_operational_data(df):
    df = df.copy()

    np.random.seed(42)

    # Simulated operational fields for prototype evaluation
    df["scheduled_procedures_7d"] = np.random.poisson(
        5, len(df)
    )

    df["alternative_available"] = np.random.choice(
        [0, 1],
        size=len(df),
        p=[0.35, 0.65]
    )

    df["alternative_capacity"] = np.random.randint(
        0, 11, len(df)
    )

    df["repair_estimate_days"] = np.random.randint(
        1, 31, len(df)
    )

    # Estimated procedures affected by downtime
    df["affected_service_load"] = (
        df["scheduled_procedures_7d"]
        * df["services_disrupted"]
    )

    return df


def generate_recommendation(row):
    """
    Generate a maintenance recommendation
    using clinical impact and operational constraints.
    """

    required_fields = [
        "scheduled_procedures_7d",
        "alternative_available",
        "alternative_capacity",
        "repair_estimate_days"
    ]

    # Safe fallback
    for field in required_fields:
        if pd.isna(row[field]):
            return (
                "REVIEW REQUIRED",
                "Operational data missing"
            )

    # High impact + no alternative
    if (
        row["clinical_impact_score"] >= 70
        and row["alternative_available"] == 0
    ):
        return (
            "URGENT",
            "High clinical impact and no alternative available"
        )

    # Scheduled workload exceeds alternative capacity
    if (
        row["scheduled_procedures_7d"]
        > row["alternative_capacity"]
        and row["clinical_impact_score"] >= 50
    ):
        return (
            "URGENT",
            "Scheduled workload exceeds alternative capacity"
        )

    # Long repair estimate + clinical impact
    if (
        row["repair_estimate_days"] > 14
        and row["clinical_impact_score"] >= 50
    ):
        return (
            "HIGH",
            "Long repair estimate with significant clinical impact"
        )

    # Clinical impact levels
    if row["clinical_impact_score"] >= 70:
        return (
            "HIGH",
            "High clinical impact"
        )

    if row["clinical_impact_score"] >= 40:
        return (
            "MEDIUM",
            "Moderate clinical impact"
        )

    return (
        "LOW",
        "Low clinical impact"
    )