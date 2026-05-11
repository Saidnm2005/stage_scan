import requests as re
import os
from dotenv import load_dotenv
load_dotenv()
api_url = os.getenv("BASE_URL")
def add_alert(payload):
    try:
        response = re.post(f"{api_url}/alerts", json=payload)
        return response.json()
    except re.RequestException as e:
        print(f"Error adding alert: {e}")
        return {"error": str(e)}
def get_alert(alert_id):
    try:
        response = re.get(f"{api_url}/alerts/{alert_id}")
        return response.json()
    except re.RequestException as e:
        print(f"Error fetching alert: {e}")
        return {"error": str(e)}
def get_alerts():
    try:
        response = re.get(f"{api_url}/alerts")
        return response.json()
    except re.RequestException as e:
        print(f"Error fetching alerts: {e}")
        return {"error": str(e)}    
def update_alert(alert_id, payload):
    try:
        response = re.put(f"{api_url}/alerts/{alert_id}", json=payload)
        return response.json()
    except re.RequestException as e:
        print(f"Error updating alert: {e}")
        return {"error": str(e)}    
def delete_alert(alert_id):
    try:
        response = re.delete(f"{api_url}/alerts/{alert_id}")
        return response.json()
    except re.RequestException as e:
        print(f"Error deleting alert: {e}")
        return {"error": str(e)}