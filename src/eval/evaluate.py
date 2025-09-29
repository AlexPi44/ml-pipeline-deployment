import pandas as pd
from sklearn.metrics import accuracy_score, f1_score
import yaml
import sys

def main():
    config_path = sys.argv[1] if len(sys.argv) > 1 else "configs/dev.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    df = pd.read_parquet(f"s3://{config['s3']['features_bucket']}/eval.parquet")
    X = df.drop('target', axis=1)
    y = df['target']
    # Load model (placeholder)
    # model = ...
    # predictions = model.predict(X)
    predictions = y  # Dummy for template
    accuracy = accuracy_score(y, predictions)
    f1 = f1_score(y, predictions, average='weighted')
    print(f"Accuracy: {accuracy}")
    print(f"F1 Score: {f1}")

if __name__ == "__main__":
    main()
