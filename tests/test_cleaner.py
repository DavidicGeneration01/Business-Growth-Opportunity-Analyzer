import pandas as pd

from src.cleaner import DataCleaner


def test_cleaner_removes_duplicates_and_standardizes_text():
    data = pd.DataFrame(
        {
            "CompanyID": ["bg-00001", "bg-00001"],
            "CompanyName": [" apex labs ", " apex labs "],
            "Industry": ["technology", "technology"],
            "Country": ["united states", "united states"],
            "YearsOperating": [5, 5],
            "Employees": [100, 100],
            "MonthlyRevenue": [100000, 100000],
            "MonthlyExpenses": [70000, 70000],
            "MarketingBudget": [5000, 5000],
            "NewCustomers": [100, 100],
            "RepeatCustomers": [300, 300],
            "CustomerSatisfaction": [15, 15],
            "EmployeeTurnover": [-5, -5],
            "ProductInnovation": [9, 9],
            "MarketShare": [10, 10],
            "RevenueGrowth": [35, 35],
            "ProfitMargin": [30, 30],
        }
    )

    cleaned = DataCleaner().clean(data)

    assert len(cleaned) == 1
    assert cleaned.loc[0, "CompanyID"] == "BG-00001"
    assert cleaned.loc[0, "CompanyName"] == "Apex Labs"
    assert cleaned.loc[0, "CustomerSatisfaction"] == 10
    assert cleaned.loc[0, "EmployeeTurnover"] == 0
