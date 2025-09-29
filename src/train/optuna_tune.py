import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import optuna
import argparse
import yaml
import boto3

def load_data(data_path):
    if data_path.startswith('s3://'):
        # Download from S3 to local temp file
        import tempfile, os
        s3 = boto3.client('s3')
        bucket = data_path.split('/')[2]
        key = '/'.join(data_path.split('/')[3:])
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            s3.download_fileobj(bucket, key, tmp)
            tmp_path = tmp.name
        df = pd.read_parquet(tmp_path)
        os.remove(tmp_path)
    else:
        if data_path.endswith('.csv'):
            df = pd.read_csv(data_path)
        else:
            df = pd.read_parquet(data_path)
    return df

def objective(trial, X_train, y_train):
    n_estimators = trial.suggest_int('n_estimators', 50, 200)
    max_depth = trial.suggest_int('max_depth', 3, 15)
    min_samples_split = trial.suggest_int('min_samples_split', 2, 10)
    min_samples_leaf = trial.suggest_int('min_samples_leaf', 1, 5)
    max_features = trial.suggest_categorical('max_features', ['sqrt', 'log2', None])
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_split=min_samples_split,
        min_samples_leaf=min_samples_leaf,
        max_features=max_features,
        random_state=42
    )
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
    return cv_scores.mean()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', required=True, help='Path to training data (csv or parquet, local or s3)')
    parser.add_argument('--target', default='target', help='Target column name')
    args = parser.parse_args()

    df = load_data(args.data)
    X = df.drop(args.target, axis=1)
    y = df[args.target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    study = optuna.create_study(direction='maximize')
    study.optimize(lambda trial: objective(trial, X_train, y_train), n_trials=50)

    best_params = study.best_params
    print(f"Best parameters: {best_params}")
    print(f"Best cross-validation score: {study.best_value:.4f}")

    best_model = RandomForestClassifier(**best_params, random_state=42)
    best_model.fit(X_train, y_train)
    y_pred = best_model.predict(X_test)
    test_accuracy = accuracy_score(y_test, y_pred)
    print(f"Test set accuracy: {test_accuracy:.4f}")
    print("Classification Report:")
    print(classification_report(y_test, y_pred))

if __name__ == "__main__":
    main()