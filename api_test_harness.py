"""
End-to-end API integration test for a migration management service.

This script simulates a complete user workflow via the REST API, including:
  0. Authenticating to get a JWT token.
  1. Creating credential and workload objects.
  2. Defining a migration target.
  3. Creating and initiating a migration task.
  4. Polling for the migration's final status.

Prerequisites:
    - The Django development server must be running.
    - The Celery worker must be running.
    - The Redis server must be available.
    - A user (e.g., superuser) must exist in the database.
"""
import time
import requests
import sys
from getpass import getpass 

# Script configuration
BASE_URL = "http://127.0.0.1:8000/api/v1"
POLL_INTERVAL_SECONDS = 2
MAX_POLL_ATTEMPTS = 15


def make_request(method, endpoint, json_data=None, token=None):
    """Wraps the requests library to perform an API call and handle errors."""
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    try:
        response = requests.request(method, url, json=json_data, headers=headers)
        response.raise_for_status()
        # Handle 204 No Content for DELETE requests
        return response.json() if response.status_code != 204 else None
    except requests.exceptions.RequestException as e:
        print(f"\nERROR: Request to {method.upper()} {url} failed.")
        print(f"   Reason: {e}")
        if e.response is not None:
            print(f"   Response Body: {e.response.text}")
        sys.exit(1)

def get_auth_token(username, password):
    """Authenticates with username/password to get a JWT access token."""
    print("\n--- Authenticating to get JWT token ---")
    auth_payload = {"username": username, "password": password}
    token_data = make_request("POST", "/token/", auth_payload)
    if not token_data or "access" not in token_data:
        print("ERROR: 'access' token not found in authentication response.")
        sys.exit(1)
    print("Authentication successful.")
    return token_data["access"]


def main():
    """Runs the main end-to-end test scenario."""
    print("Starting API Test Harness...")
    
    # Step 0 - Authentication
    username = input("Enter your Django superuser username: ")
    password = getpass("Enter your Django superuser password: ")
    access_token = get_auth_token(username, password)

    # Step 1: Create Credentials
    print("\n--- Step 1: Creating Credentials ---")
    source_creds_payload = {"username": "harness_source_user", "password": "secure_password_1"}
    target_creds_payload = {"username": "harness_target_user", "password": "secure_password_2"}
    source_creds = make_request("POST", "/credentials/", source_creds_payload, token=access_token)
    target_creds = make_request("POST", "/credentials/", target_creds_payload, token=access_token)
    print("Source and Target credentials created successfully.")

    # Step 2: Create Source and Target Workloads
    print("\n--- Step 2: Creating Source and Target Workloads ---")
   
    source_workload_payload = {
        "name": "E2E Test Source Server", "ip_address": "192.168.1.102",
        "credentials": source_creds['id'],
        "mount_points": [{"name": "C:\\", "size_gb": 100}, {"name": "D:\\", "size_gb": 500}]
    }
    target_workload_payload = {
        "name": "E2E Test Target VM", "ip_address": "10.0.0.102",
        "credentials": target_creds['id'], "mount_points": []
    }
 
    source_workload = make_request("POST", "/workloads/", source_workload_payload, token=access_token)
    target_workload = make_request("POST", "/workloads/", target_workload_payload, token=access_token)
    print("Source and Target workloads created successfully.")
    
    c_drive = next(mp for mp in source_workload['mount_points'] if mp['name'] == "C:\\")

    # Step 3: Create Migration Target
    print("\n--- Step 3: Creating Migration Target ---")
    migration_target_payload = {
        "cloud_type": "aws", "cloud_credentials": target_creds['id'],
        "target_vm": target_workload['id']
    }
 
    migration_target = make_request("POST", "/migration-targets/", migration_target_payload, token=access_token)
    print("Migration Target created successfully.")

    # Step 4: Create and Run Migration
    print("\n--- Step 4: Creating and Running Migration ---")
    migration_payload = {
        "source": source_workload['id'], "target": migration_target['id'],
        "selected_mount_points": [c_drive['id']]
    }

    migration = make_request("POST", "/migrations/", migration_payload, token=access_token)
    migration_id = migration['id']
    print(f"Migration created with ID: {migration_id}")

    run_response = make_request("POST", f"/migrations/{migration_id}/run/", token=access_token)
    print(f"Migration run command sent. Initial status: {run_response['state']}")

    # Step 5: Monitor Migration Status
    print("\n--- Step 5: Monitoring migration status ---")
    for i in range(MAX_POLL_ATTEMPTS):
        print(f"   Polling attempt {i + 1}/{MAX_POLL_ATTEMPTS}...")
        
        migration_status = make_request("GET", f"/migrations/{migration_id}/", token=access_token)
        current_state = migration_status['state']

        if current_state in ("success", "error"):
            print(f"Migration finished with state: {current_state.upper()}")
            if current_state == "success":
                print("\nTEST PASSED! End-to-end migration successful.")
            else:
                print("\nTEST FAILED! Migration ended in ERROR state.")
            sys.exit(0 if current_state == "success" else 1)

        time.sleep(POLL_INTERVAL_SECONDS)

    print("\nTEST FAILED! Migration did not complete in the allotted time.")
    sys.exit(1)


if __name__ == "__main__":
    main()
