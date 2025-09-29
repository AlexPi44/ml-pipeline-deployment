from aws_cdk import (
    Stack,
    aws_cloudwatch as cloudwatch,
    aws_sns as sns,
    aws_cloudwatch_actions as cw_actions,
    Duration
)
from constructs import Construct
class MonitoringStack(Stack):
    def __init__(self, scope: Construct, id: str, compute_stack, storage_stack, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.alert_topic = sns.Topic(
            self, "MLAlertTopic",
            display_name="ML Pipeline Alerts",
            topic_name="ml-alerts"
        )
        self.alert_topic.add_subscription(
            sns.subscriptions.EmailSubscription("oncall@example.com")
        )
        self.latency_alarm = cloudwatch.Alarm(
            self, "ModelLatencyAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/SageMaker",
                metric_name="ModelLatency",
                dimensions_map={
                    "EndpointName": "ml-endpoint",
                    "VariantName": "AllTraffic"
                }
            ),
            threshold=500,
            evaluation_periods=2,
            datapoints_to_alarm=2,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            alarm_description="Model latency exceeds 500ms"
        )
        self.latency_alarm.add_alarm_action(
            cw_actions.SnsAction(self.alert_topic)
        )
        self.error_alarm = cloudwatch.Alarm(
            self, "ModelErrorAlarm",
            metric=cloudwatch.Metric(
                namespace="ML/Inference",
                metric_name="ErrorRate",
                statistic="Average"
            ),
            threshold=0.02,
            evaluation_periods=3,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            alarm_description="Model error rate exceeds 2%"
        )
        self.error_alarm.add_alarm_action(
            cw_actions.SnsAction(self.alert_topic)
        )
        self.cost_alarm = cloudwatch.Alarm(
            self, "MLCostAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/Billing",
                metric_name="EstimatedCharges",
                dimensions_map={
                    "Currency": "USD"
                },
                statistic="Maximum",
                period=Duration.days(1)
            ),
            threshold=500,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            alarm_description="Daily ML costs exceed $500"
        )
        self.cost_alarm.add_alarm_action(
            cw_actions.SnsAction(self.alert_topic)
        )
        self.dashboard = cloudwatch.Dashboard(
            self, "MLDashboard",
            dashboard_name="ml-pipeline-dashboard",
            widgets=[
                cloudwatch.GraphWidget(
                    title="Model Latency",
                    left=[cloudwatch.Metric(
                        namespace="AWS/SageMaker",
                        metric_name="ModelLatency",
                        dimensions_map={"EndpointName": "ml-endpoint"}
                    )]
                ),
                cloudwatch.GraphWidget(
                    title="Error Rate",
                    left=[cloudwatch.Metric(
                        namespace="ML/Inference",
                        metric_name="ErrorRate"
                    )]
                ),
                cloudwatch.SingleValueWidget(
                    title="Total Inferences Today",
                    metrics=[cloudwatch.Metric(
                        namespace="ML/Inference",
                        metric_name="InferenceCount",
                        statistic="Sum"
                    )]
                ),
                cloudwatch.SingleValueWidget(
                    title="Estimated Daily Cost",
                    metrics=[cloudwatch.Metric(
                        namespace="ML/Inference",
                        metric_name="Cost",
                        statistic="Sum"
                    )]
                )
            ]
        )
