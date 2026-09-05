# Clinical-Impact-Aware Equipment Downtime Dashboard

## 1. Problem

Home-care and healthcare providers may record equipment downtime
without quantifying the clinical impact of the downtime.

A device with long downtime may not always create the highest clinical
risk, while a device with shorter downtime may affect many patients or
disrupt an important clinical service.

This project provides a prototype dashboard that combines equipment
downtime with clinical impact and operational information to support
maintenance prioritization.

---

## 2. Objective

The objective is to prioritize equipment maintenance based on:

- Equipment downtime
- Equipment availability
- Clinical service disruption
- Patients affected
- Scheduled procedures
- Alternative availability
- Alternative capacity
- Repair estimate

The system produces HIGH, MEDIUM and LOW maintenance priorities.

---

## 3. Dataset

The prototype uses a 10,000-record medical equipment maintenance dataset.

Dataset characteristics:

- Records: 10,000
- Features: 34
- Equipment and maintenance information
- Downtime information
- Clinical service disruption
- Patient impact information

Operational scheduling fields such as scheduled procedures,
alternative capacity and repair estimates were simulated for prototype
evaluation because these fields are not available in the source dataset.

These simulated fields do not represent real patient schedules.

---

## 4. Clinical Impact Score

The prototype uses a transparent rule-based scoring approach.

Clinical Impact Score:

    30%  Downtime
    25%  Patient Impact
    25%  Service Disruption
    20%  Equipment Availability

The score is converted into:

- HIGH: score >= 70
- MEDIUM: score >= 40
- LOW: score < 40

These weights are prototype assumptions and should be validated with
clinical and maintenance stakeholders before production use.

---

## 5. Operational Recommendation

The dashboard additionally considers:

- Scheduled procedures in the next 7 days
- Alternative availability
- Alternative capacity
- Repair estimate

Examples:

HIGH clinical impact + no alternative
    -> URGENT

Scheduled workload > alternative capacity
    -> URGENT

Long repair estimate + significant clinical impact
    -> HIGH

---

## 6. Dashboard Features

The Streamlit dashboard provides:

- Total equipment count
- High-priority equipment count
- Service disruption count
- Patients affected
- Department filtering
- Priority filtering
- Maintenance priority ranking
- Equipment drill-down
- Clinical impact score
- Operational evidence
- Maintenance recommendation
- Recommendation reason

---

## 7. Baseline Experiment

A baseline strategy was created using downtime only.

The proposed strategy ranks equipment using the Clinical Impact Score.

Top 20 equipment were compared.

### Baseline - Downtime Only

Patients affected: 23

Service disruptions: 8

### Proposed - Clinical Impact Score

Patients affected: 250

Service disruptions: 20

### Observed Difference

Patient impact coverage improvement: 986.96%

Service disruption coverage improvement: 150%

This experiment measures how much patient/service impact is represented
within the top 20 maintenance priorities.

The result should not be interpreted as clinical accuracy because this
prototype does not contain real prospective clinical outcomes.

---

## 8. Safe Fallback

The system should not make a trusted operational recommendation when
required operational information is missing.

If required operational data is unavailable, the recommendation can
fall back to:

    REVIEW REQUIRED

The recommendation should then be reviewed by an appropriate human
operator.

---

## 9. Limitations

This is a prototype and not a clinical decision-support system.

Limitations include:

1. Operational scheduling fields are simulated.
2. No real patient scheduling data is used.
3. Clinical impact weights are prototype assumptions.
4. The dataset does not represent live equipment status.
5. Recommendations require human review.
6. The system does not replace biomedical engineering or clinical
   decision-making.
7. No causal relationship between downtime and patient outcomes is
   established.
8. Freshness of operational data must be validated before production use.

---

## 10. Real-World Failure Cases

The system could fail in real operations if:

### Case 1 - Stale equipment status

A device may be marked unavailable even after repair.

Risk:
The system may incorrectly prioritize the equipment.

Mitigation:
Show data freshness and require status verification.

### Case 2 - Alternative equipment unavailable

The system may indicate that an alternative exists, but the alternative
may already be occupied.

Risk:
The recommendation may underestimate clinical disruption.

Mitigation:
Use real-time alternative capacity before making the recommendation.

### Case 3 - Unexpected urgent procedure

A scheduled procedure may not represent emergency demand.

Risk:
Actual clinical workload may be higher than the dashboard estimate.

Mitigation:
Human review is required for urgent clinical situations.

### Case 4 - Incorrect repair estimate

A repair may take longer than estimated because of unavailable spare
parts.

Risk:
Maintenance planning may be overly optimistic.

Mitigation:
Update repair estimates when maintenance information changes.

---

## 11. Technology

- Python
- Pandas
- NumPy
- Scikit-learn
- Streamlit
- Jupyter Notebook

---

## 12. Project Structure

    clinical-impact-downtime-dashboard/
    |
    +-- api/
    +-- dashboard/
    |   +-- app.py
    |
    +-- data/
    |   +-- equipment_district_hospital.csv
    |
    +-- docs/
    +-- experiments/
    |   +-- baseline_vs_clinical.py
    |
    +-- notebooks/
    |   +-- 01_EDA.ipynb
    |
    +-- src/
    |   +-- scoring.py
    |   +-- operational.py
    |
    +-- tests/
    +-- README.md

---

## 13. Running the Dashboard

Activate the virtual environment and run:

    streamlit run dashboard/app.py

The application will open in the local browser.

---

## 14. Prototype Status

Current prototype includes:

- Dataset analysis
- Clinical impact scoring
- Maintenance prioritization
- Operational simulation
- Dashboard
- Drill-down evidence
- Baseline comparison
- Safe recommendation logic

This prototype represents an initial implementation and is not intended
for direct clinical deployment.