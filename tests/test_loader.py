import pandas as pd
import pytest

from src.data_loader import DataLoader


def test_loader_rejects_missing_required_columns(tmp_path):
    path = tmp_path / "bad.csv"
    pd.DataFrame({"CompanyID": ["BG-00001"]}).to_csv(path, index=False)

    with pytest.raises(ValueError):
        DataLoader().load(path)
