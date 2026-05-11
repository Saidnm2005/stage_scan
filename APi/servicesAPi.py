import requests as re
url="http://localhost:8000/api/services"


def get_services():
    try:
        response = re.get(url)
        return response.json()
    except re.RequestException as e:
        print(f"Error fetching services: {e}")
        return {"error": str(e)}
    


def get_service(service_id):
    try:
        response = re.get(url + f"/{service_id}")
        return response.json()
    except re.RequestException as e:
        print(f"Error fetching service: {e}")
        return {"error": str(e)}
    


def add_service(service_data):
    try:
        response = re.post(url, json=service_data)
        return response.json()
    except re.RequestException as e:
        print(f"Error adding service: {e}")
        return {"error": str(e)}    
    

def update_service(service_id, service_data):
    try:
        response = re.put(url + f"/{service_id}", json=service_data)
        return response.json()
    except re.RequestException as e:
        print(f"Error updating service: {e}")
        return {"error": str(e)}
    

    
def delete_service(service_id):
    try:
        response = re.delete(url + f"/{service_id}")
        return response.json()
    except re.RequestException as e:
        print(f"Error deleting service: {e}")
        return {"error": str(e)}