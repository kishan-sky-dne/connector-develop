#!/bin/bash
# Set all Connectors Concourse pipelines
#
# Usage:
#   ./set-all-pipelines.sh
#
# This creates 5 separate pipelines for clean UI navigation:
# - connectors-pr         (PR checks - auto-trigger)
# - connectors-develop    (develop env - auto-trigger)
# - connectors-test       (test env - manual trigger)
# - connectors-stage      (stage env - manual trigger)
# - connectors-prod       (prod env - manual trigger)

set -euo pipefail

CONCOURSE_TARGET="dne"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "Setting Connectors Concourse Pipelines"
echo "=========================================="

# Function to set a pipeline
set_pipeline() {
  local pipeline_name=$1
  local config_file=$2
  
  echo ""
  echo "→ Setting pipeline: ${pipeline_name}"
  echo "  Config: ${config_file}"
  
  fly -t "${CONCOURSE_TARGET}" set-pipeline \
    --pipeline "${pipeline_name}" \
    --config "${config_file}" \
    --non-interactive
  
  echo "✓ Pipeline '${pipeline_name}' set successfully"
}

# Set PR checks pipeline
set_pipeline "connectors-pr" "${SCRIPT_DIR}/pipeline-pr-checks.yml"

# Set environment pipelines
set_pipeline "connectors-develop" "${SCRIPT_DIR}/pipeline-develop.yml"
set_pipeline "connectors-test" "${SCRIPT_DIR}/pipeline-test.yml"
set_pipeline "connectors-stage" "${SCRIPT_DIR}/pipeline-stage.yml"
set_pipeline "connectors-prod" "${SCRIPT_DIR}/pipeline-prod.yml"

echo ""
echo "=========================================="
echo "✓ All pipelines set successfully!"
echo "=========================================="
echo ""
echo "Pipeline URLs:"
echo "  PR Checks:  https://concourse.at.sky/teams/${CONCOURSE_TARGET}/pipelines/connectors-pr"
echo "  Develop:    https://concourse.at.sky/teams/${CONCOURSE_TARGET}/pipelines/connectors-develop"
echo "  Test:       https://concourse.at.sky/teams/${CONCOURSE_TARGET}/pipelines/connectors-test"
echo "  Stage:      https://concourse.at.sky/teams/${CONCOURSE_TARGET}/pipelines/connectors-stage"
echo "  Production: https://concourse.at.sky/teams/${CONCOURSE_TARGET}/pipelines/connectors-prod"
echo ""
echo "To unpause all pipelines:"
echo "  fly -t ${CONCOURSE_TARGET} unpause-pipeline -p connectors-pr"
echo "  fly -t ${CONCOURSE_TARGET} unpause-pipeline -p connectors-develop"
echo "  fly -t ${CONCOURSE_TARGET} unpause-pipeline -p connectors-test"
echo "  fly -t ${CONCOURSE_TARGET} unpause-pipeline -p connectors-stage"
echo "  fly -t ${CONCOURSE_TARGET} unpause-pipeline -p connectors-prod"
echo ""
echo "  Production: https://concourse.at.sky/teams/${CONCOURSE_TARGET}/pipelines/connectors-prod"
echo ""
echo "To unpause all pipelines:"
echo "  fly -t ${CONCOURSE_TARGET} unpause-pipeline -p connectors-pr"
echo "  fly -t ${CONCOURSE_TARGET} unpause-pipeline -p connectors-develop"
echo "  # fly -t ${CONCOURSE_TARGET} unpause-pipeline -p connectors-test"
echo "  # fly -t ${CONCOURSE_TARGET} unpause-pipeline -p connectors-stage"
echo "  # fly -t ${CONCOURSE_TARGET} unpause-pipeline -p connectors-prod"
echo ""
