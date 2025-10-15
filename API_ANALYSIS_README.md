# API Analysis Scripts

This directory contains reusable Python scripts for analyzing the Scorebuddy OpenAPI documentation.

## Scripts

### 1. `analyze_api.py`
General purpose API endpoint analyzer.

**Usage:**
```bash
# List all available endpoint types
python analyze_api.py --list

# Analyze specific endpoint type (e.g., groups, teams, users)
python analyze_api.py --type groups
python analyze_api.py --type teams
python analyze_api.py --type users

# Analyze all endpoints
python analyze_api.py
```

**Features:**
- Lists all available endpoint types in the API
- Analyzes specific endpoint types for PUT operations
- Shows schemas, parameters, and references
- Provides comprehensive summary

### 2. `detailed_endpoint_analysis.py`
Detailed analysis of PUT endpoints for specific resource types.

**Usage:**
```bash
# Get detailed PUT information for specific endpoint type
python detailed_endpoint_analysis.py --type groups
python detailed_endpoint_analysis.py --type teams
python detailed_endpoint_analysis.py --type users

# Show all PUT endpoints in the API
python detailed_endpoint_analysis.py --all
```

**Features:**
- Detailed PUT endpoint analysis
- Request body schemas and properties
- Response codes and descriptions
- Available schemas and parameters
- Other HTTP methods for the same endpoints

## Examples

### Analyze Groups Endpoints
```bash
python analyze_api.py --type groups
python detailed_endpoint_analysis.py --type groups
```

### Analyze Teams Endpoints
```bash
python analyze_api.py --type teams
python detailed_endpoint_analysis.py --type teams
```

### List All Available Endpoint Types
```bash
python analyze_api.py --list
```

## Benefits

- **Reusable**: Use the same scripts for any endpoint type
- **Comprehensive**: Get complete API information quickly
- **Automated**: No need to manually search through large JSON files
- **Consistent**: Same analysis format for all endpoints
- **Time-saving**: Quickly understand API structure before writing tests

These scripts will be essential for automating load tests for all remaining endpoints:
- teams
- users  
- staff
- integrations
- scorecards
- scores
- And any future endpoints
