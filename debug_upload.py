#!/usr/bin/env python3
"""
Quick test to debug the file upload error
"""

import requests
import io

BASE_URL = "https://d5857de7-ad68-4c10-b47a-b69d277d3a86.preview.emergentagent.com/api"

# Create a test plant first
plant_data = {"name": "Debug Plant", "plant_type": "Test"}
response = requests.post(f"{BASE_URL}/plants", json=plant_data)
plant_id = response.json()["id"]

print(f"Created test plant: {plant_id}")

# Test invalid file upload
try:
    files = {'file': ('test.txt', io.StringIO('not an image'), 'text/plain')}
    response = requests.post(f"{BASE_URL}/detect-disease/{plant_id}", files=files)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"Error: {str(e)}")

# Cleanup
requests.delete(f"{BASE_URL}/plants/{plant_id}")