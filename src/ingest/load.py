import pandas as pd
import boto3
import yaml

def load_data(config_path):
    with open(config_path) as f:
        config = yaml.safe_load(f)
    s3 = boto3.client('s3')
    df = pd.read_parquet(f"s3://{config['s3']['raw_bucket']}/data.parquet")
    print(f"Loaded {len(df)} records")
    return df
