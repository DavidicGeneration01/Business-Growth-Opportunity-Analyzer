import pandas as pd

from src.analysis import BusinessAnalyzer


def test_industry_summary_groups_metrics():
    data = pd.DataFrame(
        {
            "CompanyID": ["A", "B"],
            "Industry": ["Technology", "Technology"],
            "BGPI": [80, 60],
            "MonthlyRevenue": [1000, 2000],
            "ProfitMargin": [20, 10],
            "CustomerSatisfaction": [9, 7],
            "ProductInnovation": [8, 6],
            "RiskScore": [20, 40],
        }
    )

    summary = BusinessAnalyzer().industry_summary(data)

    assert summary.loc[0, "Industry"] == "Technology"
    assert summary.loc[0, "Companies"] == 2
    assert summary.loc[0, "AverageBGPI"] == 70
