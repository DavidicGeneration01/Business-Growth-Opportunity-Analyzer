# Business Growth Opportunity Analyzer

Python project for generating fictional company data, cleaning and validating it, calculating the Business Growth Potential Index (BGPI), producing statistical analysis, charts, reports, and a Streamlit dashboard.

## Overview

- Generates 5,000 realistic fictional companies.
- Cleans duplicates, missing values, numeric ranges, text fields, and IQR outliers.
- Calculates BGPI, risk score, repeat customer rate, and growth category.
- Exports descriptive statistics, industry summaries, company summaries, rankings, and correlation matrices.
- Generates 12 PNG charts with Matplotlib and Seaborn.
- Produces CSV, Excel, and PDF reports.
- Includes a multi-page Streamlit dashboard with company, industry, growth, correlation, reporting, and download views.

# Development Environment

- Python
- Jupyter Notebook
- Pandas
- Numpy
- Matplotlib
- Streamlit
- docker

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run the Complete Pipeline

```bash
py -m src.main
```

## Run the Dashboard

```bash
py -m streamlit run src/dashboard.py
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

# Useful Websites

* [LinkedIn learning](http://https://www.linkedin.com/learning/python-for-data-science-and-machine-learning-essential-training-part-1?u=2153100)
* [LinkedIn learning](https://www.linkedin.com/learning/advanced-pandas-2021?u=2153100)
* [LinkedIn learning](https://www.linkedin.com/learning/data-cleaning-and-manipulating-with-python-in-excel?u=2153100)
* [Youtube - ciao.football](https://www.youtube.com/watch?v=VzL1lw1B3UI&list=PL7uOLIiQqtTttfZYJA7c95u2Ktt_eIzP9&index=4)
* [Youtube - ciao.football](https://www.youtube.com/watch?v=z-BGa0RiGWs&list=PL7uOLIiQqtTttfZYJA7c95u2Ktt_eIzP9&index=10&pp=iAQB)
* [Youtube - ciao.football](https://www.youtube.com/watch?v=Xqs8T4W_YiI&list=PL7uOLIiQqtTttfZYJA7c95u2Ktt_eIzP9&index=7)
* [Youtube - ciao.football](https://www.youtube.com/watch?v=VuZtkGJeWR0&list=PL7uOLIiQqtTttfZYJA7c95u2Ktt_eIzP9&index=6)
* [Youtube - ciao.football](https://www.youtube.com/watch?v=A232z0HG7MA&list=PL7uOLIiQqtTttfZYJA7c95u2Ktt_eIzP9&index=5)



