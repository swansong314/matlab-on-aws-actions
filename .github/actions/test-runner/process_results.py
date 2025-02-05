#!/usr/bin/env python3
import sys

def process_test_results(report_file):
    """Simple test results processor"""
    try:
        with open(report_file, 'r') as f:
            results = f.read()
        
        # Check if all tests passed
        return 'FAILED' not in results
            
    except Exception as e:
        print(f"Error processing test results: {str(e)}", file=sys.stderr)
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: process_results.py <test_report_file>", file=sys.stderr)
        sys.exit(1)
    
    success = process_test_results(sys.argv[1])
    sys.exit(0 if success else 1)
