import pandas as pd
from src.validation.validators import validate

def test_schema_pass():
    df = pd.DataFrame({
        "feature1": [1.0],
        "feature2": [2.0],
        "target": [1]
    })
    validate(df)
