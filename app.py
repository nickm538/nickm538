# app.py
import os
import requests
from flask import Flask, render_template, request, redirect, url_for
from bs4 import BeautifulSoup
from googleapiclient.discovery import build

app = Flask(__name__)

# It's recommended to set the API key as an environment variable
# For example: export API_KEY='your_api_key'
API_KEY = os.environ.get("API_KEY")
FACT_CHECK_DISCOVERY_URL = "https://factchecktools.googleapis.com/$discovery/rest?version=v1alpha1"

def get_fact_check_service():
    if not API_KEY:
        return None
    return build("factchecktools", "v1alpha1", developerKey=API_KEY, discoveryServiceUrl=FACT_CHECK_DISCOVERY_URL)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check():
    url = request.form.get('url')
    if not url:
        return "No URL provided.", 400

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
    except requests.exceptions.RequestException as e:
        return f"Error fetching URL: {e}", 400

    soup = BeautifulSoup(response.text, 'html.parser')
    page_text = soup.get_text()

    service = get_fact_check_service()
    if not service:
        return "API_KEY not configured. Please set the environment variable.", 500

    try:
        request_body = {
            'query': page_text,
            'pageSize': 10,
        }
        fact_check_request = service.claims().search(body=request_body)
        fact_check_response = fact_check_request.execute()
        claims = fact_check_response.get('claims', [])
    except Exception as e:
        return f"Error calling Fact Check API: {e}", 500

    return render_template('results.html', url=url, claims=claims)


if __name__ == '__main__':
    app.run(debug=True)