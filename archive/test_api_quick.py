#!/usr/bin/env python3
"""
Quick API test
"""

import requests
import json

def test_api():
    try:
        # Test the KPI endpoint
        response = requests.get("http://127.0.0.1:5000/admin/api/dashboard/kpis")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("API Response:")
            print(json.dumps(data, indent=2))
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    test_api()
