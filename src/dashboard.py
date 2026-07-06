"""Interactive Streamlit dashboard."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

from config.config import AppConfig
from src.analysis import BusinessAnalyzer


CONFIG = AppConfig()


@st.cache_data
def load_dashboard_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def apply_filters(data: pd.DataFrame) -> pd.DataFrame:
    """Apply sidebar filters to dashboard data."""

    st.sidebar.header("Filters")
    companies = st.sidebar.multiselect("Company", sorted(data["CompanyName"].unique()))
    industries = st.sidebar.multiselect("Industry", sorted(data["Industry"].unique()))
    countries = st.sidebar.multiselect("Country", sorted(data["Country"].unique()))
    employee_range = st.sidebar.slider(
        "Employee range",
        int(data["Employees"].min()),
        int(data["Employees"].max()),
        (int(data["Employees"].min()), int(data["Employees"].max())),
    )
    revenue_range = st.sidebar.slider(
        "Revenue range",
        float(data["MonthlyRevenue"].min()),
        float(data["MonthlyRevenue"].max()),
        (float(data["MonthlyRevenue"].min()), float(data["MonthlyRevenue"].max())),
    )
    bgpi_range = st.sidebar.slider(
        "BGPI range",
        0.0,
        100.0,
        (float(data["BGPI"].min()), float(data["BGPI"].max())),
    )

    filtered = data.copy()
    if companies:
        filtered = filtered[filtered["CompanyName"].isin(companies)]
    if industries:
        filtered = filtered[filtered["Industry"].isin(industries)]
    if countries:
        filtered = filtered[filtered["Country"].isin(countries)]
    filtered = filtered[filtered["Employees"].between(*employee_range)]
    filtered = filtered[filtered["MonthlyRevenue"].between(*revenue_range)]
    filtered = filtered[filtered["BGPI"].between(*bgpi_range)]
    return filtered


def main() -> None:
    st.set_page_config(page_title="Business Growth Analyzer", layout="wide")
    st.title("Business Growth Opportunity Analyzer")

    data_path = CONFIG.bgpi_scores_path
    if not Path(data_path).exists():
        st.error("Run `python -m src.main` first to generate dashboard data.")
        st.stop()

    data = load_dashboard_data(str(data_path))
    filtered = apply_filters(data)
    analyzer = BusinessAnalyzer(CONFIG)

    pages = [
        "🏠 Overview",
        "📊 Company Analysis",
        "🏢 Industry Analysis",
        "📈 Growth Dashboard",
        "📉 Correlation Analysis",
        "📋 Reports",
        "⬇ Download Center",
    ]
    page = st.sidebar.radio("Page", pages)

    if page == "🏠 Overview":
        overview(filtered)
    elif page == "📊 Company Analysis":
        company_analysis(filtered)
    elif page == "🏢 Industry Analysis":
        st.dataframe(analyzer.industry_summary(filtered), use_container_width=True)
    elif page == "📈 Growth Dashboard":
        growth_dashboard(filtered)
    elif page == "📉 Correlation Analysis":
        correlation_analysis(filtered, analyzer)
    elif page == "📋 Reports":
        reports_page(filtered, analyzer)
    else:
        download_center(filtered)


def overview(data: pd.DataFrame) -> None:
    cols = st.columns(4)
    cols[0].metric("Companies", f"{len(data):,}")
    cols[1].metric("Average BGPI", f"{data['BGPI'].mean():.2f}")
    cols[2].metric("Average Revenue", f"${data['MonthlyRevenue'].mean():,.0f}")
    cols[3].metric("Average Risk", f"{data['RiskScore'].mean():.2f}")
    st.bar_chart(data.groupby("Industry")["BGPI"].mean())
    st.dataframe(data.nlargest(20, "BGPI"), use_container_width=True)


def company_analysis(data: pd.DataFrame) -> None:
    company = st.selectbox("Select company", sorted(data["CompanyName"].unique()))
    row = data[data["CompanyName"] == company].iloc[0]
    cols = st.columns(5)
    cols[0].metric("BGPI", f"{row['BGPI']:.2f}")
    cols[1].metric("Risk", f"{row['RiskScore']:.2f}")
    cols[2].metric("Profit Margin", f"{row['ProfitMargin']:.2f}%")
    cols[3].metric("Revenue Growth", f"{row['RevenueGrowth']:.2f}%")
    cols[4].metric("Category", row["GrowthCategory"])
    st.dataframe(row.to_frame("Value"), use_container_width=True)


def growth_dashboard(data: pd.DataFrame) -> None:
    st.subheader("Growth Potential")
    st.bar_chart(data["GrowthCategory"].value_counts())
    st.scatter_chart(data, x="RevenueGrowth", y="BGPI", color="Industry")


def correlation_analysis(data: pd.DataFrame, analyzer: BusinessAnalyzer) -> None:
    corr = analyzer.correlation_matrix(data)
    st.dataframe(corr, use_container_width=True)
    fig, ax = plt.subplots(figsize=(11, 7))
    sns.heatmap(corr, cmap="vlag", center=0, ax=ax)
    ax.set_title("Correlation Heatmap")
    st.pyplot(fig)


def reports_page(data: pd.DataFrame, analyzer: BusinessAnalyzer) -> None:
    st.subheader("Rankings")
    tabs = st.tabs(["Growth", "Profitability", "Innovation", "Satisfaction"])
    rankings = analyzer.company_rankings(data)
    tabs[0].dataframe(rankings["growth_potential"], use_container_width=True)
    tabs[1].dataframe(rankings["profitability"], use_container_width=True)
    tabs[2].dataframe(rankings["innovation"], use_container_width=True)
    tabs[3].dataframe(rankings["customer_satisfaction"], use_container_width=True)


def download_center(data: pd.DataFrame) -> None:
    st.download_button(
        "Download filtered CSV",
        data.to_csv(index=False),
        file_name="filtered_business_growth_data.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()
