# Bluestock Mutual Fund Analytics

A Python-based data ingestion and quality-checking project for analysing Indian mutual fund data. This project prepares datasets for downstream analysis of fund performance, NAV trends, investor transactions, SIP inflows, and portfolio holdings.

## Project Objectives

- Ingest and inspect 10 mutual fund CSV datasets using Pandas.
- Examine dataset dimensions, data types, sample records, and missing values.
- Validate AMFI scheme codes between the fund master and NAV history datasets.
- Fetch live mutual fund NAV data from the MFAPI API.
- Record data-quality observations and API inconsistencies.

## Tech Stack

- Python 3
- Pandas
- NumPy
- Requests
- Matplotlib
- Seaborn
- Plotly
- SQLAlchemy
- SciPy
- Jupyter Notebook

## Project Structure

```text
bluestock-mutual-fund-analytics/
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
├── sql/
├── dashboard/
├── reports/
├── Documentation/
├── data_ingestion.py
├── live_nav_fetch.py
├── download_datasets.py
├── inspect_datasets.py
├── requirements.txt
└── README.md
```

## Setup

Clone the repository:

```bash
git clone https://github.com/shantam-sharma/bluestock-mutual-fund-analytics.git
cd bluestock-mutual-fund-analytics
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Place the 10 supplied CSV datasets in `data/raw/`.

## Running the Scripts

Inspect the original datasets:

```bash
python inspect_datasets.py
```

Run data ingestion and quality checks:

```bash
python data_ingestion.py
```

Fetch live NAV data:

```bash
python live_nav_fetch.py
```

## Data Quality Results

The ingestion script successfully loaded all 10 original datasets.

- Fund master: 40 records.
- NAV history: 46,000 records.
- Investor transactions: 32,778 records.
- AMFI validation: PASS in both directions.
- Missing values: 12 in `yoy_growth_pct` in the monthly SIP inflows dataset.

The detailed quality summary is available in `reports/data_quality_summary.txt`.

## Live NAV API

Live NAV data is retrieved from [MFAPI](https://api.mfapi.in/).

Five requested large-cap fund schemes passed scheme-identity validation. The supplied HDFC Top 100 scheme code (`125497`) returned SBI Small Cap Fund metadata instead. This mismatch is recorded in `reports/live_nav_fetch_issues.txt`, and the returned data is not labelled as HDFC data.

## Notes

- Raw datasets are excluded from Git where configured in `.gitignore`; obtain the supplied datasets separately when required.
- The `data/processed/`, `notebooks/`, `sql/`, and `dashboard/` directories are reserved for subsequent analysis and development.

## Author

**Aayush Kumar Shantam**

GitHub: [shantam-sharma](https://github.com/shantam-sharma)
