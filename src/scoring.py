import pandas as pd


def calculate_clinical_impact(df):
    df = df.copy()

    # Normalize downtime
    max_downtime = max(df["downtime_days_last_6m"].max(), 1)

    df["downtime_score"] = (
        df["downtime_days_last_6m"] / max_downtime
    ) * 100

    # Normalize patient impact
    max_patients = max(
        df["patients_referred_equipment_down"].max(), 1
    )

    df["patient_impact_score"] = (
        df["patients_referred_equipment_down"] / max_patients
    ) * 100

    # Clinical service disruption
    df["service_impact_score"] = (
        df["services_disrupted"] * 100
    )

    # Equipment currently unavailable
    df["availability_score"] = (
        (1 - df["currently_functional"]) * 100
    )

    # Clinical Impact Score
    df["clinical_impact_score"] = (
        0.30 * df["downtime_score"]
        + 0.25 * df["patient_impact_score"]
        + 0.25 * df["service_impact_score"]
        + 0.20 * df["availability_score"]
    )

    # Priority
    def get_priority(score):
        if score >= 70:
            return "HIGH"
        elif score >= 40:
            return "MEDIUM"
        return "LOW"

    df["priority"] = df["clinical_impact_score"].apply(
        get_priority
    )

    return df