import requests

url = "http://localhost:8000/api/"

def add_asset(asset_data):
    try:
        response = requests.post(url + "assets", json=asset_data)
        return response.json()
    except requests.RequestException as e:
        print(f"Error adding asset: {e}")
        return {"error": str(e)}

def get_assets():
    try:
        response = requests.get(url + "assets")
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching assets: {e}")
        return {"error": str(e)}

def get_asset(asset_id):
    try:
        response = requests.get(url + f"assets/{asset_id}")
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching asset: {e}")
        return {"error": str(e)}



def get_asset_count():
    try:
        response = requests.get(url + "assets/count")
        data = response.json()
        return data.get("count", 0)
    except requests.RequestException as e:
        print(f"Error fetching asset count: {e}")
        return 0
    
def get_asset_details(asset_id):
    try:
        response = requests.get(url + f"assets/{asset_id}/details")
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching asset details: {e}")
        return {"error": str(e)}


def get_assets_with_issues():
    try:
        response = requests.get(url + f"assets-with-issues")
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return {"error": str(e)}

