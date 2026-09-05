import pandas as pd
import sys
import os

# Import project scoring logic
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "src")
    )
)

from scoring import calculate_clinical_impact


# -----------------------------------
# Load dataset
# -----------------------------------

DATA_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "data",
    "equipment_district_hospital.csv"
)

df = pd.read_csv(DATA_PATH)


# -----------------------------------
# Calculate clinical impact
# -----------------------------------

df = calculate_clinical_impact(df)


# -----------------------------------
# Baseline strategy
# Highest downtime first
# -----------------------------------

baseline_top20 = (
    df.sort_values(
        "downtime_days_last_6m",
        ascending=False
    )
    .head(20)
)


# -----------------------------------
# Proposed strategy
# Highest clinical impact first
# -----------------------------------

clinical_top20 = (
    df.sort_values(
        "clinical_impact_score",
        ascending=False
    )
    .head(20)
)


# -----------------------------------
# Compare patient impact
# -----------------------------------

baseline_patients = int(
    baseline_top20[
        "patients_referred_equipment_down"
    ].sum()
)

clinical_patients = int(
    clinical_top20[
        "patients_referred_equipment_down"
    ].sum()
)


# -----------------------------------
# Compare service disruptions
# -----------------------------------

baseline_disruptions = int(
    baseline_top20[
        "services_disrupted"
    ].sum()
)

clinical_disruptions = int(
    clinical_top20[
        "services_disrupted"
    ].sum()
)


# -----------------------------------
# Improvement
# -----------------------------------

patient_improvement = (
    (clinical_patients - baseline_patients)
    / max(baseline_patients, 1)
) * 100


disruption_improvement = (
    (clinical_disruptions - baseline_disruptions)
    / max(baseline_disruptions, 1)
) * 100


# -----------------------------------
# Results
# -----------------------------------

print("=" * 55)
print("BASELINE VS CLINICAL-IMPACT-AWARE EXPERIMENT")
print("=" * 55)

print("\nTop 20 equipment comparison")

print("\nBASELINE - Downtime Only")
print(
    "Patients affected:",
    baseline_patients
)
print(
    "Service disruptions:",
    baseline_disruptions
)

print("\nPROPOSED - Clinical Impact Score")
print(
    "Patients affected:",
    clinical_patients
)
print(
    "Service disruptions:",
    clinical_disruptions
)

print("\nImprovement")
print(
    "Patient impact coverage:",
    round(patient_improvement, 2),
    "%"
)

print(
    "Service disruption coverage:",
    round(disruption_improvement, 2),
    "%"
)

print("\nExperiment completed.")