#!/usr/bin/env python3
"""
Script to import and activate n8n workflow
"""

import requests
import json
import sys

def main():
    # Check if n8n is running (try health endpoint first)
    try:
        response = requests.get('http://localhost:5678/healthz', timeout=5)
        if response.status_code != 200:
            print("Error: n8n health check failed (status code: {})".format(response.status_code))
            return False
    except requests.exceptions.RequestException as e:
        print("Error: Cannot connect to n8n at http://localhost:5678 - {}".format(str(e)))
        return False

    print("✓ n8n instance is running at http://localhost:5678")

    # Load workflow JSON
    try:
        with open('n8n_automation_workflow_fixed.json', 'r') as f:
            workflow_data = json.load(f)
    except FileNotFoundError:
        print("Error: Workflow file n8n_automation_workflow_fixed.json not found")
        return False
    except json.JSONDecodeError as e:
        print("Error: Invalid JSON in workflow file - {}".format(str(e)))
        return False

    # Import workflow
    try:
        import_response = requests.post(
            'http://localhost:5678/rest/workflows',
            json=workflow_data,
            timeout=30
        )

        if import_response.status_code == 200:
            workflow_info = import_response.json()
            workflow_id = workflow_info.get('id')
            workflow_name = workflow_info.get('name', 'Unknown')
            print("✓ Workflow '{}' imported successfully with ID: {}".format(workflow_name, workflow_id))
        else:
            print("Error: Failed to import workflow (status code: {}, response: {})".format(
                import_response.status_code, import_response.text))
            return False

    except requests.exceptions.RequestException as e:
        print("Error: Failed to import workflow - {}".format(str(e)))
        return False

    # Activate workflow
    try:
        activate_response = requests.post(
            'http://localhost:5678/rest/workflows/{}/activate'.format(workflow_id),
            timeout=30
        )

        if activate_response.status_code == 200:
            print("✓ Workflow '{}' activated successfully".format(workflow_name))
            return True
        else:
            print("Error: Failed to activate workflow (status code: {}, response: {})".format(
                activate_response.status_code, activate_response.text))
            return False

    except requests.exceptions.RequestException as e:
        print("Error: Failed to activate workflow - {}".format(str(e)))
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)