#!/bin/bash
set -e
DATASET=$1
PRIORITY=${2:-normal}
echo "Triggering retrain with dataset: $DATASET, priority: $PRIORITY"
python src/train/train.py --config configs/dev.yaml
