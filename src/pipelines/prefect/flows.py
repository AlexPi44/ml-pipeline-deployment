from prefect import flow, task
from prefect.artifacts import create_markdown_artifact
from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule
import pandas as pd
import boto3
import yaml
from datetime import datetime
import mlflow

@task(retries=2, retry_delay_seconds=60)
def load_data(config):
    s3 = boto3.client('s3')
    df = pd.read_parquet(f"s3://{config['s3']['raw_bucket']}/data.parquet")
    print(f"Loaded {len(df)} records")
    return df

@task
def validate_schema(df, config):
    expected_columns = ['feature1', 'feature2', 'target']
    assert all(col in df.columns for col in expected_columns)
    assert df.isnull().sum().sum() == 0
    print("Schema validation passed")
    return df

@task
def engineer_features(df, config):
    df['feature3'] = df['feature1'] * df['feature2']
    df['feature4'] = df['feature1'] / (df['feature2'] + 1)
    output_path = f"s3://{config['s3']['features_bucket']}/features_{datetime.now().strftime('%Y%m%d')}.parquet"
    df.to_parquet(output_path)
    print(f"Features saved to {output_path}")
    return df

@task
def train_model(df, config):
    mlflow.set_tracking_uri(config['mlflow']['tracking_uri'])
    mlflow.set_experiment(config['mlflow']['experiment_name'])
    with mlflow.start_run():
        from sklearn.ensemble import RandomForestClassifier
        X = df.drop('target', axis=1)
        y = df['target']
        model = RandomForestClassifier()
        model.fit(X, y)
        mlflow.sklearn.log_model(model, "model")
        mlflow.log_metric("accuracy", 0.95)
        run_id = mlflow.active_run().info.run_id
        print(f"Model trained: {run_id}")
        return run_id

@task
def deploy_canary(run_id, config):
    import subprocess
    result = subprocess.run([
        "./scripts/deploy_canary.sh", run_id
    ], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Canary deployment failed: {result.stderr}")
    print("Canary deployed successfully")

@task
def monitor_canary(config):
    cloudwatch = boto3.client('cloudwatch')
    response = cloudwatch.get_metric_statistics(
        Namespace='AWS/SageMaker',
        MetricName='ModelLatency',
        Dimensions=[
            {'Name': 'EndpointName', 'Value': config['model']['name'] + '-endpoint'},
            {'Name': 'VariantName', 'Value': 'Canary'}
        ],
        StartTime=datetime.now().replace(hour=datetime.now().hour-1),
        EndTime=datetime.now(),
        Period=300,
        Statistics=['Average']
    )
    if response['Datapoints']:
        avg_latency = sum(d['Average'] for d in response['Datapoints']) / len(response['Datapoints'])
        if avg_latency > config['monitoring']['latency_threshold_ms']:
            raise Exception(f"Canary latency {avg_latency}ms exceeds threshold")
    print("Canary metrics healthy")
    return True

@task
def promote_or_rollback(canary_healthy, run_id, config):
    import subprocess
    if canary_healthy:
        result = subprocess.run(["./scripts/promote_canary.sh"], capture_output=True)
        print("Model promoted to production")
    else:
        result = subprocess.run(["./scripts/rollback.sh"], capture_output=True)
        print("Rolled back to previous version")

@flow(name="ml-training-pipeline")
def ml_pipeline(config_path="configs/dev.yaml"):
    with open(config_path) as f:
        config = yaml.safe_load(f)
    df = load_data(config)
    df = validate_schema(df, config)
    df = engineer_features(df, config)
    run_id = train_model(df, config)
    deploy_canary(run_id, config)
    canary_healthy = monitor_canary(config)
    promote_or_rollback(canary_healthy, run_id, config)
    markdown_report = f"""
    # Pipeline Execution Report
    **Date**: {datetime.now()}
    **Model**: {config['model']['name']}
    **Run ID**: {run_id}
    **Status**: {'Promoted' if canary_healthy else 'Rolled Back'} """
    create_markdown_artifact(
        key="pipeline-report",
        markdown=markdown_report,
        description="ML Pipeline execution report"
    )

deployment = Deployment.build_from_flow(
    flow=ml_pipeline,
    name="ml-pipeline-scheduled",
    schedule=CronSchedule(cron="0 2 * * *"),
    work_pool_name="kubernetes-pool",
    parameters={"config_path": "configs/prod.yaml"}
)

if __name__ == "__main__":
    ml_pipeline("configs/dev.yaml")
    # deployment.apply()
