#!/usr/bin/env python3
"""
Script per testare direttamente l'endpoint di lista documenti
"""
import requests
import os
from dotenv import load_dotenv
import json

# Carica variabili d'ambiente
load_dotenv('../.env')

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
FILE_SEARCH_STORE_NAME = os.getenv('FILE_SEARCH_STORE_NAME')
BASE_URL = 'https://generativelanguage.googleapis.com/v1beta'

print("=" * 60)
print("Test Endpoint Lista Documenti")
print("=" * 60)
print()

# Test con la sintassi corretta dalla documentazione
url = f"{BASE_URL}/{FILE_SEARCH_STORE_NAME}/documents"
headers = {'x-goog-api-key': GEMINI_API_KEY}

print(f"URL: {url}")
print(f"Method: GET")
print()

try:
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print()
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Successo!")
        print()
        print(json.dumps(data, indent=2))
    else:
        print("❌ Errore!")
        print()
        print(response.text)
        
except Exception as e:
    print(f"❌ Eccezione: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
