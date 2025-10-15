#!/usr/bin/env python3
"""
Script to get detailed information about specific endpoint PUT operations
This script provides comprehensive analysis of PUT endpoints for any resource type
"""
import json
import argparse

def get_detailed_put_info(api_file, endpoint_type):
    """Get detailed information about PUT endpoints for a specific type"""
    try:
        with open(api_file, 'r', encoding='utf-8') as f:
            api_data = json.load(f)
    except Exception as e:
        print(f"Error reading API file: {e}")
        return
    
    print(f"=== DETAILED {endpoint_type.upper()} PUT ENDPOINTS ===\n")
    
    paths = api_data['paths']
    put_endpoints = []
    
    # Find all PUT endpoints for the specified type
    for path, methods in paths.items():
        if endpoint_type.lower() in path.lower() and 'put' in methods:
            put_endpoints.append((path, methods['put']))
    
    if not put_endpoints:
        print(f"No PUT endpoints found for {endpoint_type}")
        return
    
    for i, (path, put_info) in enumerate(put_endpoints, 1):
        print(f"{i}. PUT {path}")
        print(f"   Summary: {put_info.get('summary', 'N/A')}")
        print(f"   Description: {put_info.get('description', 'N/A')}")
        print(f"   Operation ID: {put_info.get('operationId', 'N/A')}")
        
        # Check request body
        if 'requestBody' in put_info:
            req_body = put_info['requestBody']
            print(f"   Request Body Required: {req_body.get('required', False)}")
            if 'content' in req_body and 'application/json' in req_body['content']:
                schema = req_body['content']['application/json'].get('schema', {})
                if '$ref' in schema:
                    print(f"   Schema Reference: {schema['$ref']}")
                elif 'properties' in schema:
                    print("   Schema Properties:")
                    for prop, details in schema['properties'].items():
                        prop_type = details.get('type', 'unknown')
                        prop_desc = details.get('description', 'No description')
                        print(f"     - {prop} ({prop_type}): {prop_desc}")
        
        # Check responses
        if 'responses' in put_info:
            print("   Responses:")
            for status_code, response in put_info['responses'].items():
                print(f"     {status_code}: {response.get('description', 'N/A')}")
        print()
    
    # Check what schemas are available for this endpoint type
    print(f"=== AVAILABLE {endpoint_type.upper()} SCHEMAS ===\n")
    if 'components' in api_data and 'schemas' in api_data['components']:
        schemas = api_data['components']['schemas']
        found_schemas = False
        for schema_name, schema_data in schemas.items():
            if endpoint_type.lower() in schema_name.lower():
                found_schemas = True
                print(f"Schema: {schema_name}")
                if 'properties' in schema_data:
                    print("  Properties:")
                    for prop_name, prop_data in schema_data['properties'].items():
                        prop_type = prop_data.get('type', 'unknown')
                        prop_desc = prop_data.get('description', 'No description')
                        print(f"    - {prop_name} ({prop_type}): {prop_desc}")
                print()
        
        if not found_schemas:
            print(f"No schemas found for {endpoint_type}")
    
    # Check parameters for this endpoint type
    print(f"=== AVAILABLE {endpoint_type.upper()} PARAMETERS ===\n")
    if 'components' in api_data and 'parameters' in api_data['components']:
        parameters = api_data['components']['parameters']
        found_params = False
        for param_name, param_data in parameters.items():
            if endpoint_type.lower() in param_name.lower():
                found_params = True
                print(f"Parameter: {param_name}")
                print(f"  Description: {param_data.get('description', 'N/A')}")
                print(f"  In: {param_data.get('in', 'N/A')}")
                print(f"  Required: {param_data.get('required', False)}")
                if 'schema' in param_data:
                    schema = param_data['schema']
                    print(f"  Type: {schema.get('type', 'unknown')}")
                print()
        
        if not found_params:
            print(f"No parameters found for {endpoint_type}")
    
    # Check for other methods on the same endpoints
    print(f"=== OTHER METHODS FOR {endpoint_type.upper()} ENDPOINTS ===\n")
    for path, methods in paths.items():
        if endpoint_type.lower() in path.lower():
            print(f"Endpoint: {path}")
            for method, details in methods.items():
                if method.upper() != 'PUT':
                    print(f"  {method.upper()}: {details.get('summary', 'N/A')}")
            print()

def analyze_all_put_endpoints(api_file):
    """Analyze all PUT endpoints in the API"""
    try:
        with open(api_file, 'r', encoding='utf-8') as f:
            api_data = json.load(f)
    except Exception as e:
        print(f"Error reading API file: {e}")
        return
    
    print("=== ALL PUT ENDPOINTS IN API ===\n")
    
    paths = api_data['paths']
    put_endpoints = []
    
    # Find all PUT endpoints
    for path, methods in paths.items():
        if 'put' in methods:
            put_endpoints.append((path, methods['put']))
    
    if not put_endpoints:
        print("No PUT endpoints found in the API")
        return
    
    print(f"Total PUT endpoints found: {len(put_endpoints)}\n")
    
    for i, (path, put_info) in enumerate(put_endpoints, 1):
        print(f"{i}. PUT {path}")
        print(f"   Summary: {put_info.get('summary', 'N/A')}")
        print(f"   Operation ID: {put_info.get('operationId', 'N/A')}")
        print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get detailed PUT endpoint information')
    parser.add_argument('--file', default='scorebuddy_open_api.json', help='API JSON file path')
    parser.add_argument('--type', help='Endpoint type to analyze (e.g., groups, teams, users)')
    parser.add_argument('--all', action='store_true', help='Show all PUT endpoints in the API')
    
    args = parser.parse_args()
    
    if args.all:
        analyze_all_put_endpoints(args.file)
    elif args.type:
        get_detailed_put_info(args.file, args.type)
    else:
        print("Please specify --type <endpoint_type> or --all")
        print("Example: python detailed_endpoint_analysis.py --type groups")
        print("Example: python detailed_endpoint_analysis.py --all")
