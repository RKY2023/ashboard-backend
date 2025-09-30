import requests
from bs4 import BeautifulSoup

# Router credentials
router_ip = "http://192.168.1.1"  # Change as per your router's IP
username = "admin"
password = "your_password"

# Start a sessionpy
session = requests.Session()

# Login payload (modify based on your router's authentication method)
login_payload = {
    "username": username,
    "password": password
}

# Send login request (check your router's login URL)
login_url = f"{router_ip}/login"
response = session.post(login_url, data=login_payload)

if response.status_code == 200:
    print("Login successful!")
    
    # Fetch dashboard page
    dashboard_url = f"{router_ip}/status"
    dashboard_response = session.get(dashboard_url)
    
    # Parse data using BeautifulSoup
    soup = BeautifulSoup(dashboard_response.text, "html.parser")
    
    # Example: Extract system information
    sys_info = soup.find("div", {"id": "sys_info"})
    print(sys_info.text if sys_info else "System info not found")
    
else:
    print("Login failed, check credentials!")
