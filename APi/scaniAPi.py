import requests as re
import os
from dotenv import load_dotenv
load_dotenv()
api_url = os.getenv("BASE_URL")
def add_scan(payload):
    try:
        response = re.post(f"{api_url}/scans", json=payload)
        return response.json()
    except re.RequestException as e:
        print(f"Error adding scan: {e}")
        return {"error": str(e)}
    
def get_scan(scan_id):
    try:
        response = re.get(f"{api_url}/scans/{scan_id}")
        return response.json()
    except re.RequestException as e:
        print(f"Error fetching scan: {e}")
        return {"error": str(e)}
def get_scans():
    try:
        response = re.get(f"{api_url}/scans")
        return response.json()
    except re.RequestException as e:
        print(f"Error fetching scans: {e}")
        return {"error": str(e)}
def update_scan(scan_id, payload):
    try:
        response = re.put(f"{api_url}/scans/{scan_id}", json=payload)
        return response.json()
    except re.RequestException as e:
        print(f"Error updating scan: {e}")
        return {"error": str(e)}    
def delete_scan(scan_id):
    try:
        response = re.delete(f"{api_url}/scans/{scan_id}")
        return response.json()
    except re.RequestException as e:
        print(f"Error deleting scan: {e}")
        return {"error": str(e)}
    


def get_scan_results(scan_id):
    try:
        response = re.get(f"{api_url}/scans/{scan_id}/results")
        return response.json()
    except re.RequestException as e:
        print(f"Error fetching scan results: {e}")
        return {"error": str(e)}