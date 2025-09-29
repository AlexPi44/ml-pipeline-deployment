import boto3
import argparse

def check_canary_metrics(threshold_error_rate, threshold_latency):
    cloudwatch = boto3.client('cloudwatch')
    error_rate = cloudwatch.get_metric_statistics(
        Namespace='ML/Inference',
        MetricName='ErrorRate',
        Period=300,
        Statistics=['Average'],
        StartTime='2025-09-29T00:00:00Z',
        EndTime='2025-09-29T23:59:59Z'
    )
    latency = cloudwatch.get_metric_statistics(
        Namespace='AWS/SageMaker',
        MetricName='ModelLatency',
        Period=300,
        Statistics=['Average'],
        StartTime='2025-09-29T00:00:00Z',
        EndTime='2025-09-29T23:59:59Z'
    )
    error_avg = sum([d['Average'] for d in error_rate['Datapoints']]) / len(error_rate['Datapoints']) if error_rate['Datapoints'] else 0
    latency_avg = sum([d['Average'] for d in latency['Datapoints']]) / len(latency['Datapoints']) if latency['Datapoints'] else 0
    if error_avg > threshold_error_rate:
        print(f"Error rate {error_avg} exceeds threshold {threshold_error_rate}")
        exit(1)
    if latency_avg > threshold_latency:
        print(f"Latency {latency_avg} exceeds threshold {threshold_latency}")
        exit(1)
    print("Canary metrics healthy")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--threshold-error-rate', type=float, required=True)
    parser.add_argument('--threshold-latency', type=float, required=True)
    args = parser.parse_args()
    check_canary_metrics(args.threshold_error_rate, args.threshold_latency)
