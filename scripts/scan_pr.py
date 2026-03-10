import sys
import os
import requests
import json

# The ephemeral Basalt Shield API endpoint
BASALT_URL = "http://localhost:8000/api/v1/scan"

def scan_file(filepath):
    print(f"Scanning {filepath} for prompt injection...")
    
    if not os.path.exists(filepath):
        print(f"File {filepath} not found. Skipping.")
        return True

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    payload = {
        "text": content,
        "metadata": {
            "source": f"the_agency_pr_{filepath}"
        }
    }

    try:
        response = requests.post(BASALT_URL, json=payload, timeout=30)
        
        if response.status_code != 200:
            print(f"[!] Error: Basalt Shield API returned status {response.status_code}")
            print(response.text)
            return False
            
        result = response.json()
        
        # Basalt Shield uses a boolean `is_malicious` or similar flag.
        # Check standard AI security schema fields
        is_malicious = result.get("is_malicious", False) or result.get("injection_detected", False)
        
        if is_malicious:
            print(f"[🚨] ALERT: Prompt Injection detected in {filepath}!")
            print(f"Details: {json.dumps(result, indent=2)}")
            return False
            
        print(f"[✓] {filepath} passed security scan.")
        return True

    except requests.exceptions.RequestException as e:
        print(f"[!] Critical Error: Could not connect to Basalt Shield API at {BASALT_URL}.")
        print(f"Exception: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scan_pr.py <file1> <file2> ...")
        sys.exit(0)
        
    files_to_scan = sys.argv[1:]
    all_passed = True
    
    for file in files_to_scan:
        if file.startswith("skills/") and file.endswith(".md"):
            passed = scan_file(file)
            if not passed:
                all_passed = False
                
    if not all_passed:
        print("\n[❌] SECURITY VIOLATION: One or more SKILL.md files contained malicious prompt injection logic. PR BLOCKED.")
        sys.exit(1)
    else:
        print("\n[✅] All skills passed Basalt Shield security validation.")
        sys.exit(0)
