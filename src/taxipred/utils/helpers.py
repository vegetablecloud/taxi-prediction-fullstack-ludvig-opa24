import requests
import os 
from urllib.parse import urljoin

API_BASE_URL = os.getenv("API_URL", "http://api:8000") 

def read_api_endpoint(endpoint = "/", base_url = API_BASE_URL):
    url = urljoin(base_url, endpoint)
    response = requests.get(url)
    
    return response

def post_api_endpoint(endpoint = "/", base_url = API_BASE_URL, json = None):
    url = urljoin(base_url, endpoint)
    response = requests.post(url, json=json)
    return response