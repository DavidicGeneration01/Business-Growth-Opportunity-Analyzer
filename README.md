# Business Growth Opportunity Analyzer

Python project for generating fictional company data, cleaning and validating it, calculating the Business Growth Potential Index (BGPI), producing statistical analysis, charts, reports, and a Streamlit dashboard.

## Features

- Generates 5,000 realistic fictional companies.
- Cleans duplicates, missing values, numeric ranges, text fields, and IQR outliers.
- Calculates BGPI, risk score, repeat customer rate, and growth category.
- Exports descriptive statistics, industry summaries, company summaries, rankings, and correlation matrices.
- Generates 12 PNG charts with Matplotlib and Seaborn.
- Produces CSV, Excel, and PDF reports.
- Includes a multi-page Streamlit dashboard with company, industry, growth, correlation, reporting, and download views.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run the Complete Pipeline

```bash
python -m src.main
```

## Run the Dashboard

```bash
streamlit run src/dashboard.py
```

## Run Tests

```bash
pytest
```

## BGPI Formula

```text
BGPI =
(Profit Margin * 0.30)
+ (Revenue Growth * 0.25)
+ (Customer Satisfaction * 0.20)
+ (Product Innovation * 0.15)
+ (Repeat Customer Rate * 0.10)
- (Employee Turnover * 0.10)
```

Customer satisfaction and innovation are converted from 1-10 ratings to 0-100 scale before scoring. Final BGPI is normalized to 0-100.
