#!/usr/bin/env python3
"""
Script per creare un nuovo File Search Store
"""
import requests
import os
from dotenv import load_dotenv
import json

# Carica variabili d'ambiente
load_dotenv('../.env')

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
BASE_URL = 'https://generativelanguage.googleapis.com/v1beta'

print("=" * 60)
print("Creazione nuovo File Search Store")
print("=" * 60)
print()

# Crea nuovo store
url = f"{BASE_URL}/fileSearchStores"
headers = {
    'x-goog-api-key': GEMINI_API_KEY,
    'Content-Type': 'application/json'
}

data = {
    'displayName': 'DocumentiEgmTest - Gestione RAG'
}

print(f"URL: {url}")
print(f"Payload: {json.dumps(data, indent=2)}")
print()

try:
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    print()
    
    if response.status_code in [200, 201]:
        store_data = response.json()
        print("✅ Store creato con successo!")
        print()
        print(json.dumps(store_data, indent=2))
        print()
        print("=" * 60)
        print("📝 AGGIORNA IL FILE .env CON QUESTO VALORE:")
        print("=" * 60)
        print(f"FILE_SEARCH_STORE_NAME={store_data.get('name', 'N/A')}")
        print("=" * 60)
    else:
        print("❌ Errore nella creazione dello store")
        print(f"Response: {response.text}")
        try:
            error_data = response.json()
            print()
            print("Dettagli errore:")
            print(json.dumps(error_data, indent=2))
        except:
            pass
            
except Exception as e:
    print(f"❌ Eccezione: {e}")

print()
