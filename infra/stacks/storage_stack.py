from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_kms as kms,
    RemovalPolicy,
    Duration
)
from constructs import Construct
class StorageStack(Stack):
    def __init__(self, scope: Construct, id: str, security_stack, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.kms_key = security_stack.kms_key
        self.raw_bucket = s3.Bucket(
            self, "RawDataBucket",
            bucket_name=f"ml-{self.account}-raw-data",
            encryption=s3.BucketEncryption.KMS,
            encryption_key=self.kms_key,
            versioned=True,
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="DeleteOldVersions",
                    noncurrent_version_expiration=Duration.days(30)
                )
            ],
            removal_policy=RemovalPolicy.RETAIN
        )
        self.features_bucket = s3.Bucket(
            self, "FeaturesBucket",
            bucket_name=f"ml-{self.account}-features",
            encryption=s3.BucketEncryption.KMS,
            encryption_key=self.kms_key,
            versioned=True,
            removal_policy=RemovalPolicy.RETAIN
        )
        self.artifacts_bucket = s3.Bucket(
            self, "ArtifactsBucket",
            bucket_name=f"ml-{self.account}-artifacts",
            encryption=s3.BucketEncryption.KMS,
            encryption_key=self.kms_key,
            versioned=True,
            removal_policy=RemovalPolicy.RETAIN
        )
        self.monitoring_bucket = s3.Bucket(
            self, "MonitoringBucket",
            bucket_name=f"ml-{self.account}-monitoring",
            encryption=s3.BucketEncryption.KMS,
            encryption_key=self.kms_key,
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="DeleteOldMonitoringData",
                    expiration=Duration.days(90)
                )
            ],
            removal_policy=RemovalPolicy.DESTROY
        )
