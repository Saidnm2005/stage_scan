import requests as re
url="http://localhost:8000/api/vulnerabilities"

def get_vulnerabilities():
    try:
        response = re.get(url)
        return response.json()
    except re.RequestException as e:
        print(f"Error fetching vulnerabilities: {e}")
        return {"error": str(e)}    

def get_vulnerability(vuln_id):
    try:
        response = re.get(url + f"/{vuln_id}")
        return response.json()
    except re.RequestException as e:
        print(f"Error fetching vulnerability: {e}")
        return {"error": str(e)}
def add_vulnerability(vuln_data):
    try:
        response = re.post(url, json=vuln_data)
        return response.json()
    except re.RequestException as e:
        print(f"Error adding vulnerability: {e}")
        return {"error": str(e)}
def update_vulnerability(vuln_id, vuln_data):
    try:
        response = re.put(url + f"/{vuln_id}", json=vuln_data)
        return response.json()
    except re.RequestException as e:
        print(f"Error updating vulnerability: {e}")
        return {"error": str(e)}
def delete_vulnerability(vuln_id):
    try:
        response = re.delete(url + f"/{vuln_id}")
        return response.json()
    except re.RequestException as e:
        print(f"Error deleting vulnerability: {e}")
        return {"error": str(e)}
    
def get_vulnerability_by_cve(cve_id):
    try:
        response = re.get(url + f"/cve/{cve_id}")
        return response.json()
    except re.RequestException as e:
        print(f"Error fetching vulnerability by CVE: {e}")
        return {"error": str(e)}
    
def get_active_vuln():
    try:
        response = re.get(f"http://localhost:8000/api/active-vulnerabilitie")
        return response.json()
    except re.RequestException as e:
        print(f"Error fetching active vuln: {e}")
        return {"error": str(e)}
    
def get_critical_vuln():
    try:
        response = re.get("http://localhost:8000/api/critical-vulnerabilitie")
        return response.json()
    except re.RequestException as e:
        print(f"Error fetching data: {e}")
        return {"error": str(e)}
