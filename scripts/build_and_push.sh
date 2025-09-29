#!/bin/bash
set -e
docker build -f Dockerfile.train -t ml-train:local .
docker build -f Dockerfile.inference -t ml-inference:local .
docker push $ECR_REGISTRY/$ECR_REPO:train-latest
docker push $ECR_REGISTRY/$ECR_REPO:inference-latest
