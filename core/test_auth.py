import requests
import json
import sys

def test_auth_api():
    """Test the authentication API"""
    base_url = "http://127.0.0.1:8000/api"
    
    # Test if the server is running
    try:
        response = requests.get(base_url)
        print(f"Server status: {'OK' if response.ok else 'Error'} ({response.status_code})")
    except Exception as e:
        print(f"Server error: {str(e)}")
        print("Make sure the Django server is running.")
        return
    
    # Test admin login
    admin_credentials = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    
    try:
        print("\nTesting admin login...")
        response = requests.post(f"{base_url}/token/", json=admin_credentials)
        
        if response.ok:
            data = response.json()
            print("Admin login successful!")
            print(f"Access token: {data.get('access')[:20]}...")
            print(f"User ID: {data.get('id')}")
            print(f"Email: {data.get('email')}")
            print(f"Role: {data.get('role')}")
        else:
            print(f"Admin login failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Admin login error: {str(e)}")
    
    # Test company login
    company_credentials = {
        "email": "udayjaggumanthri@gmail.com",
        "password": "Company16@123"
    }
    
    try:
        print("\nTesting company login...")
        response = requests.post(f"{base_url}/token/", json=company_credentials)
        
        if response.ok:
            data = response.json()
            print("Company login successful!")
            print(f"Access token: {data.get('access')[:20]}...")
            print(f"User ID: {data.get('id')}")
            print(f"Email: {data.get('email')}")
            print(f"Role: {data.get('role')}")
        else:
            print(f"Company login failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Company login error: {str(e)}")
    
    # Test invalid login
    invalid_credentials = {
        "email": "invalid@example.com",
        "password": "wrongpassword"
    }
    
    try:
        print("\nTesting invalid login...")
        response = requests.post(f"{base_url}/token/", json=invalid_credentials)
        
        if not response.ok:
            print(f"Invalid login correctly failed: {response.status_code}")
            print(f"Response: {response.text}")
        else:
            print("Warning: Invalid login succeeded when it should have failed!")
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Invalid login error: {str(e)}")

if __name__ == "__main__":
    test_auth_api()
