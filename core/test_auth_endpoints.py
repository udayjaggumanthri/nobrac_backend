import requests
import json
import sys

def test_auth_endpoints():
    """Test the authentication API endpoints"""
    base_url = "http://127.0.0.1:8000/api"
    
    # Test if the server is running
    try:
        response = requests.get(base_url)
        print(f"Server status: {'OK' if response.ok else 'Error'} ({response.status_code})")
    except Exception as e:
        print(f"Server error: {str(e)}")
        print("Make sure the Django server is running.")
        return
    
    # Test admin login with the new endpoint
    admin_credentials = {
        "username": "admin@example.com",  # Using username as the frontend expects
        "password": "admin123",
        "role": "admin"
    }
    
    try:
        print("\nTesting admin login with new endpoint...")
        response = requests.post(f"{base_url}/auth/login/", json=admin_credentials)
        
        if response.ok:
            data = response.json()
            print("Admin login successful!")
            print(f"Access token: {data.get('access')[:20]}...")
            print(f"User ID: {data.get('user', {}).get('id')}")
            print(f"Email: {data.get('user', {}).get('email')}")
            print(f"Role: {data.get('user', {}).get('role')}")
            
            # Save the token for subsequent requests
            admin_token = data.get('access')
        else:
            print(f"Admin login failed: {response.status_code}")
            print(f"Response: {response.text}")
            admin_token = None
    except Exception as e:
        print(f"Admin login error: {str(e)}")
        admin_token = None
    
    # Test company login with the new endpoint
    company_credentials = {
        "username": "company@example.com",
        "password": "company123",
        "role": "company"
    }
    
    try:
        print("\nTesting company login with new endpoint...")
        response = requests.post(f"{base_url}/auth/login/", json=company_credentials)
        
        if response.ok:
            data = response.json()
            print("Company login successful!")
            print(f"Access token: {data.get('access')[:20]}...")
            print(f"User ID: {data.get('user', {}).get('id')}")
            print(f"Email: {data.get('user', {}).get('email')}")
            print(f"Role: {data.get('user', {}).get('role')}")
        else:
            print(f"Company login failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Company login error: {str(e)}")
    
    # Test volunteer login with the new endpoint
    volunteer_credentials = {
        "username": "volunteer@example.com",
        "password": "volunteer123",
        "role": "volunteer"
    }
    
    try:
        print("\nTesting volunteer login with new endpoint...")
        response = requests.post(f"{base_url}/auth/login/", json=volunteer_credentials)
        
        if response.ok:
            data = response.json()
            print("Volunteer login successful!")
            print(f"Access token: {data.get('access')[:20]}...")
            print(f"User ID: {data.get('user', {}).get('id')}")
            print(f"Email: {data.get('user', {}).get('email')}")
            print(f"Role: {data.get('user', {}).get('role')}")
        else:
            print(f"Volunteer login failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Volunteer login error: {str(e)}")
    
    # Test role mismatch (trying to login as admin with company credentials)
    role_mismatch_credentials = {
        "username": "company@example.com",
        "password": "company123",
        "role": "admin"  # Incorrect role
    }
    
    try:
        print("\nTesting role mismatch (company credentials with admin role)...")
        response = requests.post(f"{base_url}/auth/login/", json=role_mismatch_credentials)
        
        if not response.ok and response.status_code == 403:
            print("Role mismatch correctly rejected with 403 Forbidden!")
            print(f"Response: {response.text}")
        else:
            print(f"Role mismatch test failed: {response.status_code}")
            print(f"Response: {response.json() if response.ok else response.text}")
    except Exception as e:
        print(f"Role mismatch test error: {str(e)}")
    
    # Test invalid login
    invalid_credentials = {
        "username": "invalid@example.com",
        "password": "wrongpassword",
        "role": "admin"
    }
    
    try:
        print("\nTesting invalid login...")
        response = requests.post(f"{base_url}/auth/login/", json=invalid_credentials)
        
        if not response.ok and response.status_code == 401:
            print("Invalid login correctly rejected with 401 Unauthorized!")
            print(f"Response: {response.text}")
        else:
            print(f"Invalid login test failed: {response.status_code}")
            print(f"Response: {response.json() if response.ok else response.text}")
    except Exception as e:
        print(f"Invalid login test error: {str(e)}")
    
    # Test user profile endpoint (if we have an admin token)
    if admin_token:
        try:
            print("\nTesting user profile endpoint...")
            headers = {"Authorization": f"Bearer {admin_token}"}
            response = requests.get(f"{base_url}/auth/profile/", headers=headers)
            
            if response.ok:
                data = response.json()
                print("Profile retrieval successful!")
                print(f"User ID: {data.get('id')}")
                print(f"Email: {data.get('email')}")
                print(f"Role: {data.get('role')}")
            else:
                print(f"Profile retrieval failed: {response.status_code}")
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"Profile retrieval error: {str(e)}")

if __name__ == "__main__":
    test_auth_endpoints()
