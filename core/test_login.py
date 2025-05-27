import requests
import json

def test_login():
    """Test the login functionality"""
    base_url = "http://127.0.0.1:8000/api"
    
    # Test admin login
    admin_credentials = {
        "email": "admin@example.com",
        "password": "admin123",
        "role": "admin"
    }
    
    try:
        print("\nTesting admin login...")
        response = requests.post(f"{base_url}/auth/login/", json=admin_credentials)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.ok:
            data = response.json()
            print("Admin login successful!")
            print(f"Access token: {data.get('data', {}).get('access')[:20]}...")
            print(f"User role: {data.get('data', {}).get('user', {}).get('role')}")
    except Exception as e:
        print(f"Admin login error: {str(e)}")
    
    # Test company login
    company_credentials = {
        "email": "company@example.com",
        "password": "company123",
        "role": "company"
    }
    
    try:
        print("\nTesting company login...")
        response = requests.post(f"{base_url}/auth/login/", json=company_credentials)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.ok:
            data = response.json()
            print("Company login successful!")
            print(f"Access token: {data.get('data', {}).get('access')[:20]}...")
            print(f"User role: {data.get('data', {}).get('user', {}).get('role')}")
    except Exception as e:
        print(f"Company login error: {str(e)}")
    
    # Test volunteer login
    volunteer_credentials = {
        "email": "volunteer@example.com",
        "password": "volunteer123",
        "role": "volunteer"
    }
    
    try:
        print("\nTesting volunteer login...")
        response = requests.post(f"{base_url}/auth/login/", json=volunteer_credentials)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.ok:
            data = response.json()
            print("Volunteer login successful!")
            print(f"Access token: {data.get('data', {}).get('access')[:20]}...")
            print(f"User role: {data.get('data', {}).get('user', {}).get('role')}")
    except Exception as e:
        print(f"Volunteer login error: {str(e)}")

if __name__ == "__main__":
    test_login() 