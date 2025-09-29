#!/bin/bash
set -e
ENDPOINT_NAME="${MODEL_ENDPOINT:-my-model-endpoint}"
aws sagemaker update-endpoint --endpoint-name ${ENDPOINT_NAME} --endpoint-config-name ${ENDPOINT_NAME}-previous-config
echo "Rolled back to previous model version"
