#!/usr/bin/env python3
"""
Server Flask semplificato per testare solo l'endpoint documents
"""
from flask import Flask, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv('../.env')

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
FILE_SEARCH_STORE_NAME = os.getenv('FILE_SEARCH_STORE_NAME')
BASE_URL = 'https://generativelanguage.googleapis.com/v1beta'

@app.route('/api/documents', methods=['GET'])
def list_documents():
    try:
        url = f"{BASE_URL}/{FILE_SEARCH_STORE_NAME}/documents"
        headers = {'x-goog-api-key': GEMINI_API_KEY}
        
        print(f"Request to: {url}")
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        print(f"Response: {data}")
        
        return jsonify({
            'success': True,
            'documents': data.get('documents', []),
            'nextPageToken': data.get('nextPageToken', '')
        })
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print(f"Store: {FILE_SEARCH_STORE_NAME}")
    print(f"API Key configured: {bool(GEMINI_API_KEY)}")
    app.run(debug=False, host='0.0.0.0', port=5001)
