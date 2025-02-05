#!/bin/bash
set -e

echo "Starting Packer build for MATLAB ${MATLAB_RELEASE}"

cd packer/v1

# Build AMI
packer build \
  -var "matlab_release=${MATLAB_RELEASE}" \
  -var "aws_region=${AWS_REGION}" \
  template.json

# Extract AMI ID from manifest
AMI_ID=$(jq -r '.builds[-1].artifact_id' manifest.json | cut -d ":" -f2)
echo "AMI_ID=${AMI_ID}" >> $GITHUB_ENV

echo "AMI build complete: ${AMI_ID}"
