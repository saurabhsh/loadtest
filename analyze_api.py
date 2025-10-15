#!/usr/bin/env python3
"""
Script to analyze the Scorebuddy OpenAPI JSON file and extract endpoint information
This script can be reused for analyzing any endpoint type (groups, teams, users, staff, etc.)
"""
import json
import sys
import argparse

def analyze_endpoints(api_file, endpoint_type=None):
    """Analyze the API file for specific endpoint types"""
    try:
        with open(api_file, 'r', encoding='utf-8') as f:
            api_data = json.load(f)
    except Exception as e:
        print(f"Error reading API file: {e}")
        return
    
    print(f"=== {endpoint_type.upper() if endpoint_type else 'ALL'} ENDPOINTS ANALYSIS ===\n")
    
    # Check if paths exist
    if 'paths' not in api_data:
        print("No 'paths' found in API data")
        return
    
    paths = api_data['paths']
    target_endpoints = {}
    
    # Find all endpoints related to the specified type
    for path, methods in paths.items():
        if endpoint_type is None or endpoint_type.lower() in path.lower():
            target_endpoints[path] = methods
            print(f"Found {endpoint_type or 'endpoint'}: {path}")
            for method, details in methods.items():
                if method.upper() == 'PUT':
                    print(f"  PUT method found!")
                    if 'summary' in details:
                        print(f"    Summary: {details['summary']}")
                    if 'description' in details:
                        print(f"    Description: {details['description']}")
                    if 'operationId' in details:
                        print(f"    Operation ID: {details['operationId']}")
                    print()
    
    # Also check for any endpoints that might reference the target type
    if endpoint_type:
        print(f"\n=== SEARCHING FOR {endpoint_type.upper()} REFERENCES ===\n")
        for path, methods in paths.items():
            for method, details in methods.items():
                if isinstance(details, dict):
                    # Check summary, description, operationId for references
                    text_fields = ['summary', 'description', 'operationId']
                    for field in text_fields:
                        if field in details and details[field] and endpoint_type.lower() in details[field].lower():
                            print(f"Found {endpoint_type} reference in {path} {method.upper()}:")
                            print(f"  {field}: {details[field]}")
                            if method.upper() == 'PUT':
                                print(f"  *** PUT METHOD WITH {endpoint_type.upper()} REFERENCE ***")
                            print()
    
    # Check schemas for the target type
    if endpoint_type:
        print(f"\n=== {endpoint_type.upper()} SCHEMAS ===\n")
        if 'components' in api_data and 'schemas' in api_data['components']:
            schemas = api_data['components']['schemas']
            for schema_name, schema_data in schemas.items():
                if endpoint_type.lower() in schema_name.lower():
                    print(f"Found {endpoint_type} schema: {schema_name}")
                    if 'properties' in schema_data:
                        print("  Properties:")
                        for prop_name, prop_data in schema_data['properties'].items():
                            print(f"    {prop_name}: {prop_data.get('type', 'unknown')}")
                    print()
    
    # Check parameters for the target type
    if endpoint_type:
        print(f"\n=== {endpoint_type.upper()} PARAMETERS ===\n")
        if 'components' in api_data and 'parameters' in api_data['components']:
            parameters = api_data['components']['parameters']
            for param_name, param_data in parameters.items():
                if endpoint_type.lower() in param_name.lower():
                    print(f"Found {endpoint_type} parameter: {param_name}")
                    print(f"  Description: {param_data.get('description', 'N/A')}")
                    print()
    
    # Summary
    print(f"\n=== SUMMARY ===")
    print(f"Total {endpoint_type or 'endpoints'} found: {len(target_endpoints)}")
    if target_endpoints:
        print(f"{endpoint_type or 'Endpoints'}:")
        for path in target_endpoints.keys():
            print(f"  - {path}")
    else:
        print(f"No {endpoint_type or 'endpoints'} found in paths")

def list_all_endpoint_types(api_file):
    """List all available endpoint types in the API"""
    try:
        with open(api_file, 'r', encoding='utf-8') as f:
            api_data = json.load(f)
    except Exception as e:
        print(f"Error reading API file: {e}")
        return
    
    print("=== ALL AVAILABLE ENDPOINT TYPES ===\n")
    
    if 'paths' not in api_data:
        print("No 'paths' found in API data")
        return
    
    paths = api_data['paths']
    endpoint_types = set()
    
    # Extract endpoint types from paths
    for path in paths.keys():
        # Remove leading slash and split by slash
        parts = path.lstrip('/').split('/')
        if parts:
            # Get the first part (main resource)
                endpoint_types.add(parts[0])
    
    print("Available endpoint types:")
    for endpoint_type in sorted(endpoint_types):
        print(f"  - {endpoint_type}")
    
    print(f"\nTotal endpoint types: {len(endpoint_types)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze Scorebuddy OpenAPI endpoints')
    parser.add_argument('--file', default='scorebuddy_open_api.json', help='API JSON file path')
    parser.add_argument('--type', help='Endpoint type to analyze (e.g., groups, teams, users)')
    parser.add_argument('--list', action='store_true', help='List all available endpoint types')
    
    args = parser.parse_args()
    
    if args.list:
        list_all_endpoint_types(args.file)
    else:
        analyze_endpoints(args.file, args.type)
