#!/bin/bash
set -e
ENDPOINT_NAME="${MODEL_ENDPOINT:-my-model-endpoint}"
aws sagemaker update-endpoint --endpoint-name ${ENDPOINT_NAME} --endpoint-config-name ${ENDPOINT_NAME}-prod-config
echo "Canary promoted to production"
