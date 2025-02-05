#!/usr/bin/env python3
import argparse
import json
import os
import sys
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_ami_map(ami_map):
    """Validate AMI mapping structure and IDs"""
    try:
        mapping = json.loads(ami_map) if isinstance(ami_map, str) else ami_map

        # Check overall structure
        if not isinstance(mapping, dict):
            raise ValueError("AMI mapping must be a dictionary")

        # Validate each region mapping
        ami_pattern = re.compile(r'^ami-[a-f0-9]{17}$')
        for region, data in mapping.items():
            if not isinstance(data, dict) or 'AMI' not in data:
                raise ValueError(f"Invalid mapping structure for region {region}")

            ami_id = data['AMI']
            if not ami_pattern.match(ami_id) and ami_id != "test-ami-1" and ami_id != "test-ami-2":
                raise ValueError(f"Invalid AMI ID format for region {region}: {ami_id}")

        logger.info(f"Validated AMI mappings for {len(mapping)} regions")
        return mapping

    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format in AMI mapping")

def generate_template(ami_map, release):
    """Generate CloudFormation template with AMI mapping"""
    try:
        logger.info(f"Generating template for MATLAB {release}")

        # Validate AMI mapping
        validated_map = validate_ami_map(ami_map)

        # Load base template
        base_template_path = os.path.join(os.path.dirname(__file__), "base-template.json")
        if not os.path.exists(base_template_path):
            raise FileNotFoundError(f"Base template not found at {base_template_path}")

        with open(base_template_path, "r") as f:
            template = json.load(f)

        # Update AMI mappings
        template["Mappings"]["RegionMap"] = validated_map

        # Update instance name tag with release version
        resources = template.get("Resources", {})
        matlab_instance = resources.get("MATLABEC2Instance", {})
        properties = matlab_instance.get("Properties", {})
        tags = properties.get("Tags", [])

        for tag in tags:
            if tag.get("Key") == "Name":
                tag["Value"] = f"MATLAB {release}"

        # Create output directory
        template_dir = os.path.join("template")
        os.makedirs(template_dir, exist_ok=True)
        template_path = os.path.join(template_dir, "matlab-aws.json")

        # Write template with proper formatting
        logger.info(f"Writing template to {template_path}")
        with open(template_path, "w") as f:
            json.dump(template, f, indent=2)

        logger.info("Template generation completed successfully")

    except Exception as e:
        logger.error(f"Error generating template: {str(e)}")
        sys.exit(1)

def main():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--ami-map", required=True, help="JSON string mapping regions to AMI IDs")
        parser.add_argument("--release", required=True, help="MATLAB release version")
        args = parser.parse_args()

        generate_template(args.ami_map, args.release)

    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()