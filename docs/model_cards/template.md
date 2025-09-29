# Model Card: [Model Name] v[Version]
## Model Details
- **Model ID**: `[run_id]`
- **Git SHA**: `[git_sha]`
- **Training Date**: `[date]`
- **Framework**: `[framework]`
- **Architecture**: `[architecture]`
## Training Data
- **Dataset**: `s3://[bucket]/[path]`
- **Dataset Snapshot**: `[snapshot_id]`
- **Size**: `[num_samples]` samples
- **Features**: `[num_features]` features
- **Time Period**: `[start_date]` to `[end_date]`
## Evaluation Metrics
| Metric | Value | Threshold |
|--------|-------|-----------|
| Accuracy | 0.XX | > 0.90 |
| F1 Score | 0.XX | > 0.85 |
| Latency (p99) | XXms | < 500ms |
| Cost per 1k inferences | $X.XX | < $10 |
## Safety & Fairness
- **PII Detection**:
- **Bias Testing**:
- **Content Safety**:
- **Explainability Report**: `s3://[bucket]/explainability/[run_id].html`
## Limitations
- [List known limitations]
- [Edge cases]
- [Data assumptions]
## Intended Use
- **Primary Use Case**: [description]
- **Users**: [target users]
- **Out of Scope**: [what not to use for]
## Deployment
- **Endpoint**: `[endpoint_name]`
- **Instance Type**: `ml.m5.large`
- **Min Instances**: 2
- **Max Instances**: 10
- **Auto-scaling Target**: 70% CPU
## Monitoring
- **Drift Detection**: Enabled
- **Retraining Trigger**: Monthly or on drift
- **Alert Channels**: #ml-alerts, PagerDuty
## Approval
- **ML Team**:
- **Security**:
- **Product**:
@ml-lead (date)
@security-lead (date)
Pending
