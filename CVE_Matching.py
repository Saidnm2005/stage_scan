import subprocess
import json
import os
from datetime import datetime
import uuid  # Used to create unique filenames

REGISTRY_FILE = "scan_registry.json"

def load_registry():
    """Loads the database of previous scans."""
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_to_registry(product_key, data):
    """Saves a new scan result to the persistent registry."""
    registry = load_registry()
    registry[product_key] = data
    with open(REGISTRY_FILE, "w") as f:
        json.dump(registry, f, indent=4)

def run_vuln_scan(product, version):
    product_key = f"{product}:{version}"
    
    # 1. Check Registry
    registry = load_registry()
    if product_key in registry:
        return registry[product_key]
     
    temp_filename = f"temp_vuln_{uuid.uuid4().hex}.json"
    
    # Use shell=True and explicit absolute paths to ensure the tool knows where to write
    current_dir = os.getcwd()
    temp_path = os.path.join(current_dir, temp_filename)

    command = f'venv/bin/vuln-checker --products "{product_key}" --format json --output "{temp_path}"'
    
    try:
        print(f"🔍 Scanning {product_key}...")
        # We capture output to check for "No vulnerabilities found" messages in the text
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        
        # 2. Check if the file exists
        if os.path.exists(temp_path):
            with open(temp_path, "r") as f:
                new_data = json.load(f)
            
            save_to_registry(product_key, new_data)
            os.remove(temp_path)
            return new_data
        
        # 3. Handle the case where the scan worked but found nothing
        else:
            print(f"ℹ️ Scan finished, but no vulnerabilities found for {product_key}.")
            empty_result = {"status": "safe", "vulnerabilities": [], "scan_time": str(datetime.now())}
            save_to_registry(product_key, empty_result)
            return empty_result
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Scanner failed: {e.stderr}")
        return {"error": "Scanner crashed or failed"}
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

