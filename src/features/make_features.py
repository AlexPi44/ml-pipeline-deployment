import pandas as pd
import yaml
import sys
from datetime import datetime

def main():
    config_path = sys.argv[1] if len(sys.argv) > 1 else "configs/dev.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    input_path = f"s3://{config['s3']['raw_bucket']}/data.parquet"
    output_path = f"s3://{config['s3']['features_bucket']}/features_{datetime.now().strftime('%Y%m%d')}.parquet"
    df = pd.read_parquet(input_path)
    df['feature3'] = df['feature1'] * df['feature2']
    df['feature4'] = df['feature1'] / (df['feature2'] + 1)
    df.to_parquet(output_path)
    print(f"Features saved to {output_path}")

if __name__ == "__main__":
    main()
