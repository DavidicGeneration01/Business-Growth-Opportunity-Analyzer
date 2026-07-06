import pandas as pd

from src.bgpi import BGPICalculator


def test_bgpi_calculation_adds_required_outputs():
    data = pd.DataFrame(
        {
            "CompanyID": ["BG-00001", "BG-00002"],
            "CompanyName": ["A", "B"],
            "Industry": ["Technology", "Retail"],
            "Country": ["United States", "Canada"],
            "YearsOperating": [5, 10],
            "Employees": [100, 250],
            "MonthlyRevenue": [100000, 200000],
            "MonthlyExpenses": [70000, 170000],
            "MarketingBudget": [5000, 8000],
            "NewCustomers": [100, 100],
            "RepeatCustomers": [300, 50],
            "CustomerSatisfaction": [9.0, 5.0],
            "EmployeeTurnover": [8.0, 25.0],
            "ProductInnovation": [9.0, 4.0],
            "MarketShare": [10.0, 5.0],
            "RevenueGrowth": [35.0, 2.0],
            "ProfitMargin": [30.0, 15.0],
        }
    )

    scored = BGPICalculator().calculate(data)

    assert {"BGPI", "RiskScore", "GrowthCategory", "RepeatCustomerRate"}.issubset(scored.columns)
    assert scored["BGPI"].between(0, 100).all()
    assert scored.loc[0, "BGPI"] > scored.loc[1, "BGPI"]
