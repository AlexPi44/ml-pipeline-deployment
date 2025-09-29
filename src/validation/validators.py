import pandas as pd
from schema import SCHEMA

def validate(df: pd.DataFrame):
    for col, dtype in SCHEMA.items():
        assert col in df.columns, f"Missing column: {col}"
        assert df[col].dtype == dtype, f"Column {col} has wrong type"
    assert df.isnull().sum().sum() == 0, "Null values found"
    print("Schema validation passed")
