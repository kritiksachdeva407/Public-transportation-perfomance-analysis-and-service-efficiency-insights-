# Public Transportation Performance Analysis and Service Efficiency Insights

**Course/project context:** SRM Institute of Science and Technology  
**Project area:** Data Science, Exploratory Data Analysis (EDA), Business Intelligence, and Transport Performance Analytics

## Overview
This project analyses public-transport trip records to explore trip volume, route-level performance, punctuality, arrival delays, and passenger usage when passenger counts are available. It provides a Streamlit dashboard for exploring CSV data and a bundled synthetic dataset for demonstrating the application.

> **Important:** `data/sample_transit_data.csv` is synthetic demonstration data. Its values are not real transport-agency findings. Replace it with a validated public dataset before making real-world claims.

## Features
- Load the bundled demonstration CSV or upload another CSV.
- Standardize column names, parse timestamps, remove invalid required records and duplicate trip records.
- Calculate trip totals, cancellation counts, average delay, on-time rate, median delay, and 90th-percentile delay where supported by the data.
- Visualize trips by route, trips by scheduled hour, route-level average delay, and delay distribution.
- Summarize passenger counts only when that field is present.
- Preview prepared records, inspect basic data-quality checks, and download cleaned data.

## Project structure
```text
public_transportation_performance/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/
│   └── sample_transit_data.csv
└── outputs/
    └── .gitkeep
```

## Requirements
- Python 3.10 or newer recommended
- pip

## Run locally
1. Download or clone this repository.
2. Open a terminal in the project folder.
3. Create and activate a virtual environment (recommended).
   - Windows: `python -m venv .venv` then `.venv\Scripts\activate`
   - macOS/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Start the dashboard:
   ```bash
   streamlit run app.py
   ```
6. Open the local URL shown in the terminal by Streamlit.

## CSV format
The dashboard expects a CSV file with these fields:

| Column | Required? | Meaning |
|---|---|---|
| `route_id` | Yes | Route identifier |
| `scheduled_time` | Yes | Scheduled trip/arrival timestamp |
| `actual_time` | For delay KPIs | Actual timestamp; blank values are permitted |
| `trip_id` | No | Trip identifier; generated if absent |
| `cancelled` | No | `true`/`false`, `yes`/`no`, or `1`/`0` |
| `passenger_count` | No | Passenger count for demand analysis |

Timestamp examples: `2026-09-01 08:30:00`. Column names such as `route`, `scheduled`, `actual`, and `passengers` are also normalized by the app.

## KPI definitions
- **Delay (minutes):** actual time minus scheduled time. Negative values mean early arrival; positive values mean late arrival.
- **On-time rate:** percentage of non-cancelled trips with valid actual times whose delay is less than or equal to the selected threshold (default 5 minutes).
- **Average delay:** mean delay for non-cancelled trips with valid actual and scheduled times.
- **Cancellation count:** records marked cancelled.
- **Trip volume:** number of usable records, not necessarily passenger demand.
- **Passenger usage:** only reported when `passenger_count` is available and contains usable values.

The on-time threshold is a project setting, not a universal standard. Confirm the chosen definition with your instructor or dataset documentation.

## Methodology
1. Define research questions and KPIs.
2. Select and validate a public transport dataset.
3. Inspect data quality and field coverage.
4. Parse timestamps and handle missing or duplicate records.
5. Derive date, hour, weekday, and delay features.
6. Perform exploratory data analysis and calculate supported KPIs.
7. Visualize route and time-period comparisons.
8. Interpret results cautiously and make evidence-based recommendations.

## Limitations
- Actual times, cancellation indicators, passenger counts, and capacity may be missing from real datasets.
- Different operators may define punctuality differently.
- Correlation or route differences do not establish the cause of a delay.
- The included data is synthetic; use a reliable public dataset for research conclusions.

## Suggested next steps
- Select a public dataset from a transport authority or open-data portal.
- Record the dataset name, source URL, date accessed, and licence in the report.
- Validate the schema and adapt column mappings if needed.
- Run the dashboard on the real data and replace illustrative claims with measured findings.
- Add screenshots of the running dashboard to the project report/PPT.

## GitHub upload
Do not upload virtual environments, private credentials, or large unrelated files. This repository includes a `.gitignore` for common generated files. Keep the dataset's source and licence documented if you replace the sample data.
