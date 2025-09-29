from aws_cdk import (
    Stack,
    aws_ecr as ecr,
    aws_sagemaker as sagemaker,
    aws_iam as iam,
    aws_ec2 as ec2,
    RemovalPolicy
)
from constructs import Construct
class ComputeStack(Stack):
    def __init__(self, scope: Construct, id: str, network_stack, security_stack, storage_stack, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.ecr_repo = ecr.Repository(
            self, "MLRepository",
            repository_name="ml-inference",
            image_scan_on_push=True,
            removal_policy=RemovalPolicy.RETAIN,
            lifecycle_rules=[
                ecr.LifecycleRule(
                    max_image_count=10,
                    description="Keep only 10 most recent"
                )
            ]
        )
        self.sagemaker_role = iam.Role(
            self, "SageMakerExecutionRole",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess")
            ]
        )
        for bucket in [storage_stack.raw_bucket, storage_stack.features_bucket, storage_stack.artifacts_bucket, storage_stack.monitoring_bucket]:
            bucket.grant_read_write(self.sagemaker_role)
        self.sagemaker_domain = sagemaker.CfnDomain(
            self, "MLDomain",
            auth_mode="IAM",
            default_user_settings=sagemaker.CfnDomain.UserSettingsProperty(
                execution_role=self.sagemaker_role.role_arn,
                security_groups=[network_stack.sagemaker_sg.security_group_id]
            ),
            domain_name="ml-domain",
            vpc_id=network_stack.vpc.vpc_id,
            subnet_ids=[subnet.subnet_id for subnet in network_stack.vpc.private_subnets]
        )
        self.endpoint_config = sagemaker.CfnEndpointConfig(
            self, "MLEndpointConfig",
            endpoint_config_name="ml-endpoint-config",
            production_variants=[
                sagemaker.CfnEndpointConfig.ProductionVariantProperty(
                    model_name="ml-model",
                    variant_name="AllTraffic",
                    initial_instance_count=2,
                    instance_type="ml.m5.large",
                    initial_variant_weight=1.0
                )
            ]
        )
