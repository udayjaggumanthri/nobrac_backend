import requests
import json
import sys

def test_api_endpoints():
    """Test the API endpoints"""
    base_url = "http://127.0.0.1:8000/api"
    
    # Test if the server is running
    try:
        response = requests.get(base_url)
        print(f"Server status: {'OK' if response.ok else 'Error'} ({response.status_code})")
    except Exception as e:
        print(f"Server error: {str(e)}")
        print("Make sure the Django server is running.")
        return
    
    # Test the companies endpoint
    try:
        print("\nTesting companies endpoint...")
        response = requests.get(f"{base_url}/companies/")
        
        if response.ok:
            companies = response.json()
            print(f"Companies endpoint OK: {len(companies)} companies found")
            for company in companies:
                print(f"  - {company.get('name')} (ID: {company.get('id')})")
        else:
            print(f"Companies endpoint error: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Companies endpoint error: {str(e)}")
    
    # Test the auth login endpoint
    try:
        print("\nTesting auth login endpoint...")
        login_data = {
            "username": "admin@example.com",
            "password": "admin123",
            "role": "admin"
        }
        response = requests.post(f"{base_url}/auth/login/", json=login_data)
        
        if response.ok:
            data = response.json()
            print("Auth login endpoint OK")
            print(f"Access token: {data.get('access')[:20]}...")
            
            # Save the token for subsequent requests
            admin_token = data.get('access')
            headers = {"Authorization": f"Bearer {admin_token}"}
            
            # Test creating a company with the admin token
            print("\nTesting company creation...")
            company_data = {
                "name": "Test Company",
                "email": "testcompany@example.com",
                "phone": "123-456-7890",
                "industry": "Technology",
                "location": "Test Location",
                "username": "company_user@example.com",
                "password": "company123"
            }
            
            try:
                response = requests.post(f"{base_url}/companies/", json=company_data, headers=headers)
                
                if response.ok:
                    new_company = response.json()
                    print("Company creation OK")
                    print(f"Company ID: {new_company.get('id')}")
                    print(f"Company name: {new_company.get('name')}")
                    
                    # Check if user credentials are in the response
                    user_credentials = new_company.get('user_credentials')
                    if user_credentials:
                        print("User credentials found in response")
                        print(f"Username: {user_credentials.get('username')}")
                        print(f"Role: {user_credentials.get('role')}")
                    else:
                        print("Warning: No user credentials found in response")
                else:
                    print(f"Company creation error: {response.status_code}")
                    print(f"Response: {response.text}")
            except Exception as e:
                print(f"Company creation error: {str(e)}")
        else:
            print(f"Auth login endpoint error: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Auth login endpoint error: {str(e)}")

if __name__ == "__main__":
    test_api_endpoints()
