
# --- Combined ML Pipeline for Heart Disease and Telco Churn ---
import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, confusion_matrix
from sklearn.model_selection import train_test_split, cross_val_score
import optuna
import yaml
import os
from src.features.feature_engineering import get_features

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def objective(trial, X_train, y_train, model_type):
    if model_type == 'randomforest':
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
    elif model_type == 'xgboost':
        n_estimators = trial.suggest_int('n_estimators', 50, 200)
        max_depth = trial.suggest_int('max_depth', 3, 15)
        learning_rate = trial.suggest_float('learning_rate', 0.01, 0.3)
        subsample = trial.suggest_float('subsample', 0.6, 1.0)
        colsample_bytree = trial.suggest_float('colsample_bytree', 0.6, 1.0)
        model = XGBClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            subsample=subsample,
            colsample_bytree=colsample_bytree,
            random_state=42,
            use_label_encoder=False,
            eval_metric='logloss'
        )
    else:
        raise ValueError('Unknown model type')
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
    return cv_scores.mean()

def run_mlflow_pipeline(config_path, data_path, target_col, dataset, model_type):
    config = load_config(config_path)
    mlflow.set_tracking_uri(config['mlflow']['tracking_uri'])
    mlflow.set_experiment(config['mlflow']['experiment_name'])
    df = pd.read_csv(data_path)
    df = get_features(df, dataset)
    X = df.drop(target_col, axis=1)
    y = df[target_col]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    study = optuna.create_study(direction='maximize')
    study.optimize(lambda trial: objective(trial, X_train, y_train, model_type), n_trials=50)
    best_params = study.best_params
    with mlflow.start_run() as run:
        mlflow.log_params(best_params)
        if model_type == 'randomforest':
            model = RandomForestClassifier(**best_params, random_state=42)
        else:
            model = XGBClassifier(**best_params, random_state=42, use_label_encoder=False, eval_metric='logloss')
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)
        f1 = f1_score(y_test, predictions, average='weighted')
        try:
            roc_auc = roc_auc_score(y_test, predictions)
        except Exception:
            roc_auc = None
        mlflow.log_metrics({"accuracy": accuracy, "f1_score": f1, "roc_auc": roc_auc if roc_auc else 0})
        mlflow.sklearn.log_model(model, "model")
        print(f"MLflow run completed. Run ID: {run.info.run_id}")
        print(f"Best parameters: {best_params}")
        print(f"Test accuracy: {accuracy}")
        print(f"Test F1 score: {f1}")
        if roc_auc:
            print(f"Test ROC AUC: {roc_auc}")
        print("Confusion Matrix:")
        print(confusion_matrix(y_test, predictions))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='configs/dev.yaml')
    parser.add_argument('--data', default='data/heart-disease.csv')
    parser.add_argument('--target', default='target')
    parser.add_argument('--dataset', choices=['heart', 'telco'], default='heart')
    parser.add_argument('--model', choices=['randomforest', 'xgboost'], default='randomforest')
    args = parser.parse_args()
    run_mlflow_pipeline(args.config, args.data, args.target, args.dataset, args.model)
