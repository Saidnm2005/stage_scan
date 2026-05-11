import requests as re
import os
from dotenv import load_dotenv
load_dotenv()
api_url = os.getenv("BASE_URL")
def add_service_vulnerability(payload):
    try:
        response = re.post(f"{api_url}/service-vulnerabilities", json=payload)
        return response.json()
    except re.RequestException as e:
        print(f"Error adding service vulnerability: {e}")
        return {"error": str(e)}
    
def get_service_vulnerability(vuln_id):
    try:
        response = re.get(f"{api_url}/service-vulnerabilities/{vuln_id}")
        return response.json()
    except re.RequestException as e:
        print(f"Error fetching service vulnerability: {e}")
        return {"error": str(e)}
def get_service_vulnerabilities():
    try:
        response = re.get(f"{api_url}/service-vulnerabilities")
        return response.json()
    except re.RequestException as e:
        print(f"Error fetching service vulnerabilities: {e}")
        return {"error": str(e)}
def update_service_vulnerability(vuln_id, payload):
    try:
        response = re.put(f"{api_url}/service-vulnerabilities/{vuln_id}", json=payload)
        return response.json()
    except re.RequestException as e:
        print(f"Error updating service vulnerability: {e}")
        return {"error": str(e)}    
def delete_service_vulnerability(vuln_id):
    try:
        response = re.delete(f"{api_url}/service-vulnerabilities/{vuln_id}")
        return response.json()
    except re.RequestException as e:
        print(f"Error deleting service vulnerability: {e}")
        return {"error": str(e)}
