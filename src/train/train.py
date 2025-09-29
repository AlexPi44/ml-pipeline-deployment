import argparse
import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
import yaml
import boto3
import hashlib
import json
from datetime import datetime

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def compute_dataset_hash(data_path):
    """Compute hash of dataset for versioning"""
    hasher = hashlib.md5()
    with open(data_path, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def train(config_path):
    config = load_config(config_path)
    mlflow.set_tracking_uri(config['mlflow']['tracking_uri'])
    mlflow.set_experiment(config['mlflow']['experiment_name'])
    with mlflow.start_run() as run:
        import subprocess
        git_sha = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8').strip()
        mlflow.set_tag("git_sha", git_sha)
        s3 = boto3.client('s3')
        data_path = f"s3://{config['s3']['features_bucket']}/train.parquet"
        df_train = pd.read_parquet(data_path)
        dataset_hash = compute_dataset_hash(data_path)
        mlflow.set_tag("dataset_snapshot_id", dataset_hash)
        X_train = df_train.drop('target', axis=1)
        y_train = df_train['target']
        model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        mlflow.log_params({
            "n_estimators": 100,
            "max_depth": 10,
            "instance_type": config['sagemaker']['instance_type']
        })
        model.fit(X_train, y_train)
        predictions = model.predict(X_train)
        accuracy = accuracy_score(y_train, predictions)
        f1 = f1_score(y_train, predictions, average='weighted')
        mlflow.log_metrics({
            "accuracy": accuracy,
            "f1_score": f1,
            "training_samples": len(X_train)
        })
        from mlflow.models.signature import infer_signature
        signature = infer_signature(X_train, predictions)
        mlflow.sklearn.log_model(
            model,
            "model",
            signature=signature,
            registered_model_name=config['model']['name']
        )
        model_card = {
            "model_name": config['model']['name'],
            "git_sha": git_sha,
            "run_id": run.info.run_id,
            "dataset_snapshot_id": dataset_hash,
            "metrics": {
                "accuracy": accuracy,
                "f1_score": f1
            },
            "training_completed": datetime.utcnow().isoformat(),
            "config": config
        }
        s3.put_object(
            Bucket=config['s3']['artifacts_bucket'],
            Key=f"model_cards/{run.info.run_id}.json",
            Body=json.dumps(model_card)
        )
        mlflow.log_artifact("model_card.json")
        print(f"Training completed. Run ID: {run.info.run_id}")
        return run.info.run_id

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    train(args.config)
