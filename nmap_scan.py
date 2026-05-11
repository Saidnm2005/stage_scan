import nmap
import re

def is_valid_target(target):
    ip_pattern = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?:/\d{1,2})?$")
    return bool(ip_pattern.match(target))

def discover_network(network_range):
    nm = nmap.PortScanner()
    try:
        # Fast ping scan to find active IPs
        nm.scan(hosts=network_range, arguments='-sn')
        return [
            {"ip": host, "state": nm[host].state()}
            for host in nm.all_hosts()
        ]
    except Exception as e:
        return {"error": str(e)}


def scan_host_auto(target):
    nm = nmap.PortScanner()
    
    # We use exactly what worked in your terminal, 
    # but add -sV for the "Product/Version" info you want in the UI.
    # We remove -O for now to ensure maximum speed and stability.
    args = "-p- -sS -sV -Pn --privileged -T4"

    try:
        nm.scan(hosts=target, arguments=args)
        results = []
        
        if target not in nm.all_hosts():
            return {"error": f"No data found for {target}"}

        host_info = nm[target]
        addresses = host_info.get('addresses', {})
        mac = addresses.get('mac', 'N/A')
        vendor = host_info.get('vendor', {}).get(mac, 'Unknown Vendor')

        host_data = {
            "host": target,
            "hostname": host_info.hostname() or "localhost",
            "mac": mac,
            "vendor": vendor,
            "state": host_info.state(),
            "protocols": []
        }

        for proto in host_info.all_protocols():
            ports_list = []
            # This captures every port found in the scan
            for port in sorted(host_info[proto].keys()):
                svc = host_info[proto][port]
                ports_list.append({
                    "port": port,
                    "name": svc.get("name", "unknown"),
                    "product": svc.get("product", ""),
                    "version": svc.get("version", ""),
                    "state": svc.get("state", "open")
                })
            
            host_data["protocols"].append({
                "protocol": proto, 
                "ports": ports_list
            })
            
        results.append(host_data)
        return results

    except Exception as e:
        return {"error": f"Internal Error: {str(e)}"}