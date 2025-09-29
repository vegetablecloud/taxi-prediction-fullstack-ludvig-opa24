import requests 
from urllib.parse import urljoin

def read_api_endpoint(endpoint = "/", base_url = "http://api:8000"):
    url = urljoin(base_url, endpoint)
    response = requests.get(url)
    
    return response

# TODO:
# post_api_endpoint