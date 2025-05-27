import requests
import json
import sys
import time

def test_company_api():
    """Test the company API endpoints"""
    base_url = "http://127.0.0.1:8000/api"
    
    # Test if the server is running
    try:
        response = requests.get(base_url)
        print(f"Server status: {'OK' if response.ok else 'Error'} ({response.status_code})")
    except Exception as e:
        print(f"Server error: {str(e)}")
        print("Make sure the Django server is running.")
        return
    
    # Step 1: Login as admin
    admin_credentials = {
        "username": "admin@example.com",
        "password": "admin123",
        "role": "admin"
    }
    
    try:
        print("\nStep 1: Logging in as admin...")
        response = requests.post(f"{base_url}/auth/login/", json=admin_credentials)
        
        if response.ok:
            data = response.json()
            print("Admin login successful!")
            print(f"Access token: {data.get('access')[:20]}...")
            
            # Save the token for subsequent requests
            admin_token = data.get('access')
            headers = {"Authorization": f"Bearer {admin_token}"}
        else:
            print(f"Admin login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return
    except Exception as e:
        print(f"Admin login error: {str(e)}")
        return
    
    # Step 2: Create a new company
    new_company = {
        "name": "Test Company API",
        "email": "testcompany@example.com",
        "phone": "123-456-7890",
        "industry": "Technology",
        "location": "Test Location",
        "username": "company_user@example.com",
        "password": "company123"
    }
    
    try:
        print("\nStep 2: Creating a new company...")
        response = requests.post(f"{base_url}/companies/", json=new_company, headers=headers)
        
        if response.ok:
            company_data = response.json()
            company_id = company_data.get('id')
            print(f"Company created successfully with ID: {company_id}")
            print(f"Company name: {company_data.get('name')}")
            print(f"Company email: {company_data.get('email')}")
            
            # Check if user credentials are in the response
            user_credentials = company_data.get('user_credentials')
            if user_credentials:
                print("\nUser account created with credentials:")
                print(f"Username: {user_credentials.get('username')}")
                print(f"Password: {user_credentials.get('password')}")
                print(f"Role: {user_credentials.get('role')}")
                
                # Save credentials for login test
                company_username = user_credentials.get('username')
                company_password = user_credentials.get('password')
            else:
                print("Warning: No user credentials found in the response")
                company_username = new_company['username']
                company_password = new_company['password']
        else:
            print(f"Company creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return
    except Exception as e:
        print(f"Company creation error: {str(e)}")
        return
    
    # Step 3: Test login with the new company account
    company_credentials = {
        "username": company_username,
        "password": company_password,
        "role": "company"
    }
    
    try:
        print("\nStep 3: Testing login with the new company account...")
        # Wait a moment to ensure the user is fully created in the database
        time.sleep(1)
        
        response = requests.post(f"{base_url}/auth/login/", json=company_credentials)
        
        if response.ok:
            data = response.json()
            print("Company login successful!")
            print(f"Access token: {data.get('access')[:20]}...")
            print(f"User ID: {data.get('user', {}).get('id')}")
            print(f"Email: {data.get('user', {}).get('email')}")
            print(f"Role: {data.get('user', {}).get('role')}")
            
            # Save the token for company requests
            company_token = data.get('access')
            company_headers = {"Authorization": f"Bearer {company_token}"}
        else:
            print(f"Company login failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Company login error: {str(e)}")
    
    # Step 4: Get the company profile
    try:
        print("\nStep 4: Getting the company profile...")
        response = requests.get(f"{base_url}/auth/company/profile/", headers=company_headers)
        
        if response.ok:
            profile_data = response.json()
            print("Company profile retrieved successfully!")
            print(f"Company name: {profile_data.get('name')}")
            print(f"Company email: {profile_data.get('email')}")
            print(f"Company industry: {profile_data.get('industry')}")
        else:
            print(f"Company profile retrieval failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Company profile retrieval error: {str(e)}")
    
    # Step 5: Delete the company (as admin)
    try:
        print("\nStep 5: Deleting the company...")
        response = requests.delete(f"{base_url}/companies/{company_id}/", headers=headers)
        
        if response.status_code == 204:
            print("Company deleted successfully!")
        else:
            print(f"Company deletion failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Company deletion error: {str(e)}")
    
    # Step 6: Verify the company user can no longer log in
    try:
        print("\nStep 6: Verifying the company user can no longer log in...")
        response = requests.post(f"{base_url}/auth/login/", json=company_credentials)
        
        if not response.ok:
            print("Test passed: Company user can no longer log in (expected behavior)")
            print(f"Status code: {response.status_code}")
        else:
            print("Test failed: Company user can still log in after company deletion")
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Verification error: {str(e)}")

if __name__ == "__main__":
    test_company_api()
