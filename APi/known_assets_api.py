import requests as re
import os
from dotenv import load_dotenv
load_dotenv()
api_url = os.getenv("BASE_URL")

def add_known_asset(payload):
    try:
        response = re.post(f"{api_url}/known-assets", json=payload)
        return response.json()
    except re.RequestException as e:
        print(f"Error adding known asset: {e}")
        return {"error": str(e)}
def get_known_asset(asset_id):
    try:
        response = re.get(f"{api_url}/known-assets/{asset_id}")
        return response.json()
    except re.RequestException as e:
        print(f"Error fetching known asset: {e}")
        return {"error": str(e)}
def get_known_assets():
    try:
        response = re.get(f"{api_url}/known-assets")
        return response.json()
    except re.RequestException as e:
        print(f"Error fetching known assets: {e}")
        return {"error": str(e)}
def update_known_asset(asset_id, payload):
    try:
        response = re.put(f"{api_url}/known-assets/{asset_id}", json=payload)
        return response.json()
    except re.RequestException as e:
        print(f"Error updating known asset: {e}")
        return {"error": str(e)}    
def delete_known_asset(asset_id):
    try:
        response = re.delete(f"{api_url}/known-assets/{asset_id}")
        return response.json()
    except re.RequestException as e:
        print(f"Error deleting known asset: {e}")
        return {"error": str(e)}
def check_existing_asset(mac_address):
    try:
        response = re.get(f"{api_url}/known-assets/mac/{mac_address}")
        return response.status_code == 200
    except re.RequestException as e:
        print(f"Error checking existing asset: {e}")
        return False
    
def get_unknown_assets():
    try:
        response = re.get(f"{api_url}/unknown-assets")
        return response.json()
    except re.RequestException as e:
        print(f"Error checking existing asset: {e}")
        return False