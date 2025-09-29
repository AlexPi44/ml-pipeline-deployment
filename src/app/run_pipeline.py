import os
import subprocess

def run_all():
    print("Step 1: Data Ingestion...")
    subprocess.run(["python", "src/ingest/load.py", "configs/dev.yaml"])
    print("Step 2: Feature Engineering...")
    subprocess.run(["python", "src/features/make_features.py", "configs/dev.yaml"])
    print("Step 3: Data Validation...")
    subprocess.run(["python", "src/validation/validators.py"])
    print("Step 4: Hyperparameter Tuning...")
    subprocess.run(["python", "src/train/optuna_tune.py", "--data", "data/heart-disease.csv", "--target", "target"])
    print("Step 5: Model Training...")
    subprocess.run(["python", "src/train/train.py", "--config", "configs/dev.yaml"])
    print("Step 6: Model Evaluation...")
    subprocess.run(["python", "src/eval/evaluate.py", "configs/dev.yaml"])
    print("Step 7: Explainability...")
    subprocess.run(["python", "src/explainability/explain.py", "configs/dev.yaml"])
    print("Step 8: Register Model...")
    subprocess.run(["python", "src/register/register_model.py", "configs/dev.yaml"])
    print("Pipeline completed.")

if __name__ == "__main__":
    run_all()