# Runbook: Model Performance Drop
## Alert Details
- **Alert Name**: ModelPerformanceDrop
- **Severity**: P1
- **SLA**: 30 minutes response time
## Symptoms
- Model accuracy drops below 85%
- F1 score below threshold
- Increased prediction errors
## Immediate Actions
### 1. Verify Alert (5 min)
```bash
aws cloudwatch get-metric-statistics \
  --namespace ML/Inference \
  --metric-name Accuracy \
  --start-time 2025-09-29T00:00:00Z \
  --end-time 2025-09-29T23:59:59Z \
  --period 3600 \
  --statistics Average
```
### 2. Check Model Health (5 min)
```bash
curl -X POST https://api.example.com/predict \
  -H "Content-Type: application/json" \
  -d '{"input": "test_data"}'
aws sagemaker list-endpoints --name-contains ml-endpoint
```
### 3. Rollback if Critical (10 min)
```bash
./scripts/rollback.sh previous-model-config
aws sagemaker describe-endpoint --endpoint-name ml-endpoint
```
### 4. Investigate Root Cause (15 min)
```bash
python scripts/check_data_drift.py \
  --baseline s3://ml-monitoring/baseline/ \
  --current s3://ml-monitoring/current/
python scripts/validate_recent_data.py \
  --hours 24
```
### 5. Trigger Retraining if Needed
```bash
./scripts/trigger_retrain.sh \
  --dataset s3://ml-features/latest/ \
  --priority high
```
## Escalation Path
1. L1: On-call engineer (0-30 min)
2. L2: ML Team Lead (30-60 min)
3. L3: Principal Engineer (60+ min)
## Contact List
• On-call: Check PagerDuty
• ML Team: #ml-team slack
• Data Team: #data-team slack
## Post-Incident
1. Create incident report
2. Update model monitoring thresholds if needed
3. Schedule post-mortem within 48 hours
4. Update this runbook with findings
