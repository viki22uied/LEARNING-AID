#!/usr/bin/env python3
"""
Simple test script to verify the API is working
"""

import requests
import time

def test_api():
    """Test the API endpoints"""
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 Testing Open Educational Resources Recommendation Backend API")
    print("=" * 60)
    
    # Test root endpoint
    try:
        print("🔍 Testing root endpoint...")
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"✅ Root endpoint: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
    
    # Test health endpoint
    try:
        print("\n🔍 Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Health endpoint: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
    
    # Test status endpoint
    try:
        print("\n🔍 Testing status endpoint...")
        response = requests.get(f"{base_url}/api/v1/status", timeout=5)
        print(f"✅ Status endpoint: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Status endpoint failed: {e}")
    
    # Test resources endpoint
    try:
        print("\n🔍 Testing resources endpoint...")
        response = requests.get(f"{base_url}/api/v1/resources", timeout=5)
        print(f"✅ Resources endpoint: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Resources endpoint failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 API testing completed!")

if __name__ == "__main__":
    # Wait a moment for the server to start
    print("⏳ Waiting for server to start...")
    time.sleep(2)
    test_api()
