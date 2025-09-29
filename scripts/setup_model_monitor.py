import boto3
from sagemaker.model_monitor import DefaultModelMonitor, CronExpressionGenerator
from sagemaker.model_monitor.dataset_format import DatasetFormat
import yaml

def setup_model_monitor(config_path="configs/prod.yaml"):
    with open(config_path) as f:
        config = yaml.safe_load(f)
    monitor = DefaultModelMonitor(
        role=config['sagemaker']['role_arn'],
        instance_count=1,
        instance_type='ml.m5.xlarge',
        volume_size_in_gb=20,
        max_runtime_in_seconds=3600
    )
    monitor.suggest_baseline(
        baseline_dataset=f"s3://{config['s3']['features_bucket']}/baseline/",
        dataset_format=DatasetFormat.csv(header=True),
        output_s3_uri=f"s3://{config['s3']['monitoring_bucket']}/baseline/",
        wait=True
    )
    monitor.create_monitoring_schedule(
        monitor_schedule_name=f"{config['model']['name']}-monitor",
        endpoint_input=config['model']['name'] + '-endpoint',
        output_s3_uri=f"s3://{config['s3']['monitoring_bucket']}/reports/",
        statistics=monitor.baseline_statistics(),
        constraints=monitor.suggested_constraints(),
        schedule_cron_expression=CronExpressionGenerator.hourly(),
        enable_cloudwatch_metrics=True
    )
    print("Model Monitor configured successfully")

if __name__ == "__main__":
    setup_model_monitor()
