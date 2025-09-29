#!/bin/bash
set -e
DATASET_PATH=$1
SNAPSHOT_ID=$(md5sum $DATASET_PATH | awk '{print $1}')
echo "Snapshot ID: $SNAPSHOT_ID"
