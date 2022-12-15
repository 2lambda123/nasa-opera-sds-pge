#!/bin/bash

# run_metrics()
# This script wraps a "docker run" command within metrics_collection_start() and
# metrics_collection_end() function calls.
#
# usage:
#     run_metrics.sh <pge> <run config_fn> (file name only) <data_dir> (full path) <image name>
#     Eg. bash run_metrics.sh  DSWX_HLS_PGE  dswx_hls.yaml  /Users/..../test_datasets  l30_greenland  opera/proteus cal_val_3.1 5
#

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
echo "Script_dir: ${SCRIPT_DIR}"
. "${SCRIPT_DIR}"/util.sh

PGE_NAME=$1     # PGE name
RUNCONFIG=$2    # Runconfig file name (not full path)
DATA_DIR=$3     # Data directory for input and output to the docker run command
DATA_SET=$4     # Currently we have 2 datasets for dswx_hls 'l30_greenland' and 's30_louisiana
PGE_IMAGE=$5    # Name of the docker image to run stats on
PGE_TAG=$6      # Name of the docker tag
SAMPLE_TIME=$7  # Amount of time between samples (seconds)

#metrics_collection_start "$PGE_NAME" "$PGE_IMAGE" "$PGE_TAG" "$SAMPLE_TIME"
metrics_collection_start "$PGE_NAME" "$SAMPLE_TIME"

echo "Running pge '$PGE_NAME' (image $PGE_IMAGE, tag $PGE_TAG) using run config '$RUNCONFIG'"
echo "Sending 'docker run' command"

FULL_DATA_DIR="${DATA_DIR}/${DATA_SET}"
FULL_IMAGE_NAME="${PGE_IMAGE}:${PGE_TAG}"

docker run --rm -u $UID:$(id -g) \
  -v "${FULL_DATA_DIR}"/runconfig:/home/conda/runconfig:ro \
  -v "${FULL_DATA_DIR}"/input_dir:/home/conda/input_dir:ro \
  -v "${FULL_DATA_DIR}"/output_dir:/home/conda/output_dir \
  -i --tty "${FULL_IMAGE_NAME}" \
  sh -ci "python3 proteus-0.1/bin/dswx_hls.py runconfig/dswx_hls.yaml --log output_dir/l30_greenland"

docker_run_exit_code=$?
echo "Docker run exited with code: " $docker_run_exit_code

output_dir="${FULL_DATA_DIR}"/output_dir:/home/conda/output_dir
metrics_collection_end "$PGE_NAME" "$docker_run_exit_code" "$output_dir"
