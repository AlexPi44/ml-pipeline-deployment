#!/usr/bin/env python3
import os
from aws_cdk import App, Environment, Tags
from stacks.network_stack import NetworkStack
from stacks.storage_stack import StorageStack
from stacks.compute_stack import ComputeStack
from stacks.monitoring_stack import MonitoringStack
from stacks.security_stack import SecurityStack
app = App()
# Get environment from context
env_name = app.node.try_get_context("env") or "dev"
# Environment mapping
env_config = {
    "dev": {"account": "111111111111", "region": "eu-central-1"},
    "staging": {"account": "222222222222", "region": "eu-central-1"},
    "prod": {"account": "333333333333", "region": "eu-central-1"}
}
env = Environment(
    account=env_config[env_name]["account"],
    region=env_config[env_name]["region"]
)
# Create stacks
network = NetworkStack(app, f"MLPipeline-Network-{env_name}", env=env)
security = SecurityStack(app, f"MLPipeline-Security-{env_name}", env=env)
storage = StorageStack(app, f"MLPipeline-Storage-{env_name}", security_stack=security, env=env)
compute = ComputeStack(app, f"MLPipeline-Compute-{env_name}", network_stack=network, security_stack=security, storage_stack=storage, env=env)
monitoring = MonitoringStack(app, f"MLPipeline-Monitoring-{env_name}", compute_stack=compute, storage_stack=storage, env=env)
# Add tags
Tags.of(app).add("Project", "MLPipeline")
Tags.of(app).add("Environment", env_name)
Tags.of(app).add("ManagedBy", "CDK")
app.synth()
