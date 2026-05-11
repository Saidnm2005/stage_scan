import requests as re
import os
from dotenv import load_dotenv
load_dotenv()
api_url = os.getenv("BASE_URL")

def add_scan_result(payload):
    try:
        response = re.post(f"{api_url}/scan-results", json=payload)
        return response.json()
    except re.RequestException as e:
        print(f"Error adding scan: {e}")
        return {"error": str(e)}
    
def get_scan_result(scan_id):
    try:
        response = re.get(f"{api_url}/scan-results/{scan_id}")
        return response.json()
    except re.RequestException as e:
        print(f"Error fetching scan: {e}")
        return {"error": str(e)}
def get_scan_results():
    try:
        response = re.get(f"{api_url}/scan-results")
        return response.json()
    except re.RequestException as e:
        print(f"Error fetching scans: {e}")
        return {"error": str(e)}
def update_scan_result(scan_id, payload):
    try:
        response = re.put(f"{api_url}/scan-results/{scan_id}", json=payload)
        return response.json()
    except re.RequestException as e:
        print(f"Error updating scan: {e}")
        return {"error": str(e)}    
def delete_scan_result(scan_id):
    try:
        response = re.delete(f"{api_url}/scan-results/{scan_id}")
        return response.json()
    except re.RequestException as e:
        print(f"Error deleting scan: {e}")
        return {"error": str(e)}    