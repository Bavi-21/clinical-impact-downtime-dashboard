# Clinical-Impact-Aware Equipment Downtime Dashboard

## Project Overview

The Clinical-Impact-Aware Equipment Downtime Dashboard is a prototype decision-support system designed for home-care and healthcare equipment lending environments.

Traditional equipment downtime tracking mainly focuses on whether equipment is available or unavailable. However, downtime does not always have the same clinical importance.

This project improves maintenance prioritization by considering:

- Equipment downtime
- Patients affected
- Clinical service disruption
- Equipment availability
- Scheduled procedures
- Alternative equipment availability
- Alternative capacity
- Estimated repair duration

The system converts these factors into a Clinical Impact Score and uses the score to support maintenance prioritization.

---

## Problem Statement

Healthcare equipment downtime is often recorded as a technical or operational event without clearly measuring its potential clinical impact.

For example:

- Two devices may have the same downtime.
- One device may affect no patients.
- Another device may affect multiple patients and disrupt an important service.

Therefore, maintenance decisions should consider the potential clinical consequences of equipment downtime rather than relying only on downtime duration.

---

## Project Objective

The main objective is to develop a dashboard that helps maintenance and operational teams identify equipment that may require higher priority based on clinical and operational impact.

The prototype provides:

1. Clinical impact scoring
2. Maintenance priority classification
3. Operational recommendation
4. Department-level analysis
5. High-impact equipment identification
6. Equipment-level drill-down
7. Data quality monitoring
8. Safe fallback states
9. Filtered report export
10. Executive summary

---

# Clinical Impact Scoring

Each equipment record receives a Clinical Impact Score from multiple factors.

### Scoring Components

| Component | Weight |
|---|---:|
| Downtime Impact | 30% |
| Patient Impact | 25% |
| Service Disruption | 25% |
| Equipment Availability | 20% |

### Formula

Clinical Impact Score =

```text
0.30 × Downtime Score
+ 0.25 × Patient Impact Score
+ 0.25 × Service Impact Score
+ 0.20 × Availability Score