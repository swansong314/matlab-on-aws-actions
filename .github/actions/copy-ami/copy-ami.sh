#!/bin/bash
set -e

echo "Starting AMI copy process"

# Initialize AMI map with source region
AMI_MAP="{\"${SOURCE_REGION}\": {\"AMI\": \"${SOURCE_AMI_ID}\"}"

# Copy AMI to each target region
for region in ${TARGET_REGIONS//,/ }; do
  if [ "$region" != "$SOURCE_REGION" ]; then
    echo "Copying AMI to region: $region"

    # Copy AMI to target region
    COPIED_AMI=$(aws ec2 copy-image \
      --source-image-id "$SOURCE_AMI_ID" \
      --source-region "$SOURCE_REGION" \
      --region "$region" \
      --name "matlab-aws-${region}" \
      --output text --query 'ImageId')

    # Wait for AMI to be available
    aws ec2 wait image-available --region "$region" --image-ids "$COPIED_AMI"

    # Add to AMI map
    AMI_MAP="${AMI_MAP}, \"${region}\": {\"AMI\": \"${COPIED_AMI}\"}"
  fi
done

# Close JSON object
AMI_MAP="${AMI_MAP}}"

# Set output for GitHub Actions
echo "ami_map=${AMI_MAP}" >> $GITHUB_OUTPUT

echo "AMI copy process complete"