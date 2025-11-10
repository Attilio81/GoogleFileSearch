#!/usr/bin/env python3
"""
Script di test per verificare la connessione alle Google Gemini API
"""
import requests
import os
from dotenv import load_dotenv

# Carica variabili d'ambiente
load_dotenv('../.env')

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
FILE_SEARCH_STORE_NAME = os.getenv('FILE_SEARCH_STORE_NAME')
BASE_URL = 'https://generativelanguage.googleapis.com/v1beta'

print("=" * 60)
print("Test connessione Google Gemini File Search API")
print("=" * 60)
print(f"\nAPI Key: {GEMINI_API_KEY[:20]}...")
print(f"Store Name: {FILE_SEARCH_STORE_NAME}")
print()

# Test 1: Lista documenti
print("📋 Test 1: Lista documenti")
print("-" * 60)
url = f"{BASE_URL}/{FILE_SEARCH_STORE_NAME}/documents"
headers = {'x-goog-api-key': GEMINI_API_KEY}

print(f"URL: {url}")
print(f"Headers: {headers}")
print()

try:
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print()
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Successo!")
        print(f"Documenti trovati: {len(data.get('documents', []))}")
        print(f"Response: {data}")
    else:
        print("❌ Errore!")
        print(f"Response Text: {response.text}")
        try:
            error_data = response.json()
            print(f"Error JSON: {error_data}")
        except:
            pass
            
except Exception as e:
    print(f"❌ Eccezione: {e}")

print()
print("=" * 60)

# Test 2: Verifica che lo store esista
print("\n🔍 Test 2: Verifica esistenza store")
print("-" * 60)
store_url = f"{BASE_URL}/{FILE_SEARCH_STORE_NAME}"
print(f"URL: {store_url}")

try:
    response = requests.get(store_url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ Eccezione: {e}")

print()
print("=" * 60)
