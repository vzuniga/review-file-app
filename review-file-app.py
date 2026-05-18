from flask import Flask, request, jsonify, render_template
import os
import requests
import base64
import time
import json
import concurrent.futures

app = Flask(__name__)

API_KEY = 'Insert_Key_Here'
API_SECRET = 'Secret_Here'
REST_URI = 'https://Your-catalog-URL-Here:443/iii/sierra-api/v6/'
TOKEN_URL = REST_URI + 'token'

LOG_DIR = "logs"
UPDATE_LOG = os.path.join(LOG_DIR, "update_log.txt")
PATRON_LOG = os.path.join(LOG_DIR, "patron_log.txt")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

token_cache = {"access_token": None, "expires_at": 0}

def get_token():
    if token_cache['access_token'] and time.time() < token_cache['expires_at']:
        return token_cache['access_token']

    credentials = f"{API_KEY}:{API_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    headers = {'Authorization': f'Basic {encoded_credentials}'}
    response = requests.post(TOKEN_URL, headers=headers, data={'grant_type': 'client_credentials'})
    if response.ok:
        token_data = response.json()
        token_cache['access_token'] = token_data['access_token']
        token_cache['expires_at'] = time.time() + token_data['expires_in']
        return token_data['access_token']
    else:
        print("Failed to fetch token:", response.text)
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/review-files')
def get_review_files():
    token = get_token()
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(REST_URI + 'reviewFiles', headers=headers)
    if response.ok:
        all_files = response.json()
        return jsonify([f for f in all_files if f.get("recordType") == "p"])
    return jsonify([])

@app.route('/review-file/<int:file_id>')
def get_review_file(file_id):
    token = get_token()
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f"{REST_URI}reviewFiles/{file_id}/records", headers=headers)
    if response.ok:
        return jsonify(response.json())
    return jsonify({'entries': []})

def fetch_patron_record(pid, headers):
    try:
        url = f"{REST_URI}patrons/{pid}?fields=names,barcodes,addresses,emails,phones"
        start_time = time.time()
        res = requests.get(url, headers=headers)
        duration = time.time() - start_time
        if res.ok:
            return res.json(), duration
        else:
            print(f"Failed to fetch patron {pid}: {res.status_code}")
            return None, duration
    except Exception as e:
        print(f"Error fetching patron {pid}: {e}")
        return None, 0

@app.route('/patron-records', methods=['POST'])
def get_patron_records():
    ids = request.json.get('ids', [])
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 100))
    start = (page - 1) * limit
    selected_ids = [pid[1:] if isinstance(pid, str) and pid.startswith("p") else str(pid) for pid in ids[start:start + limit]]

    token = get_token()
    headers = {'Authorization': f'Bearer {token}'}
    patrons = []
    total_time = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_patron_record, pid, headers) for pid in selected_ids]
        for future in concurrent.futures.as_completed(futures):
            result, duration = future.result()
            total_time += duration
            if result:
                patrons.append(result)

    avg_time = round(total_time / max(len(selected_ids), 1), 3)
    return jsonify({'patrons': patrons, 'average_response_time': avg_time})

@app.route('/update-entry/<int:patron_id>', methods=['POST'])
def update_patron_entry(patron_id):
    data = request.get_json()
    token = get_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    url = f"{REST_URI}patrons/{patron_id}"
    try:
        res = requests.put(url, headers=headers, json=data)
        log_line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} | Patron {patron_id} | Status: {res.status_code} | Success: {res.ok} | Payload: {json.dumps(data)} | Response: {res.text}"
        with open(UPDATE_LOG, "a", encoding="utf-8") as f:
            f.write(f"{log_line}\n")
        print(log_line)
        return jsonify({'success': res.ok})
    except Exception as e:
        print(f"Update failed for patron {patron_id}: {e}")
        with open(UPDATE_LOG, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | Patron {patron_id} | ERROR: {e}\n")
        return jsonify({'success': False})

@app.route('/log-batch', methods=['POST'])
def log_batch():
    data = request.get_json()
    lines = data.get('lines', [])
    with open(PATRON_LOG, "a", encoding="utf-8") as f:
        for line in lines:
            f.write(f"{line}\n")
    return {'success': True}, 200

if __name__ == '__main__':
    app.run(debug=True)
