#!/bin/bash
set -e
IMAGE=$1
ENDPOINT_NAME="${MODEL_ENDPOINT:-my-model-endpoint}"
ENV="${ENVIRONMENT:-staging}"
CONFIG_FILE="configs/${ENV}.yaml"
CANARY_WEIGHT=$(python -c "import yaml; print(yaml.safe_load(open('$CONFIG_FILE'))['model']['canary_traffic'])")
echo "Deploying canary with ${CANARY_WEIGHT}% traffic to ${ENDPOINT_NAME}"
MODEL_NAME="${ENDPOINT_NAME}-$(date +%s)"
aws sagemaker create-model \
    --model-name ${MODEL_NAME} \
    --primary-container Image=${IMAGE} \
    --execution-role-arn ${SAGEMAKER_ROLE_ARN}
ENDPOINT_CONFIG="${MODEL_NAME}-config"
aws sagemaker create-endpoint-config \
    --endpoint-config-name ${ENDPOINT_CONFIG} \
    --production-variants \
        VariantName=Production,ModelName=${CURRENT_MODEL},InitialInstanceCount=2,InstanceType=ml.m5.large,InitialVariantWeight=$((100-CANARY_WEIGHT*100)) \
        VariantName=Canary,ModelName=${MODEL_NAME},InitialInstanceCount=1,InstanceType=ml.m5.large,InitialVariantWeight=$((CANARY_WEIGHT*100))
aws sagemaker update-endpoint \
    --endpoint-name ${ENDPOINT_NAME} \
    --endpoint-config-name ${ENDPOINT_CONFIG}
echo "Canary deployed successfully"
