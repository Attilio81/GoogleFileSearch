#!/usr/bin/env python3
"""
Script per testare l'upload di un documento
"""
import requests
import os
from dotenv import load_dotenv
import io

# Carica variabili d'ambiente
load_dotenv('../.env')

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
FILE_SEARCH_STORE_NAME = os.getenv('FILE_SEARCH_STORE_NAME')
BASE_URL = 'https://generativelanguage.googleapis.com/upload/v1beta'

print("=" * 60)
print("Test Upload Documento")
print("=" * 60)
print()

# Crea un file di test in memoria
test_content = "Questo è un documento di test per il sistema RAG.\n\nContiene informazioni importanti."
test_file = io.BytesIO(test_content.encode('utf-8'))
test_file.name = 'test_document.txt'

# URL per upload
url = f"{BASE_URL}/{FILE_SEARCH_STORE_NAME}:uploadToFileSearchStore"
headers = {'x-goog-api-key': GEMINI_API_KEY}

print(f"URL: {url}")
print(f"File: test_document.txt ({len(test_content)} bytes)")
print()

# Prepara i metadati come JSON
import json
metadata = {
    'displayName': 'Test Document Upload',
    'mimeType': 'text/plain'
}

# Prepara multipart con esattamente 2 parti
files = {
    'metadata': (None, json.dumps(metadata), 'application/json'),
    'file': ('test_document.txt', test_file, 'text/plain')
}

try:
    print("Invio richiesta...")
    response = requests.post(url, headers=headers, files=files)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print()
    
    if response.status_code in [200, 201]:
        import json
        result = response.json()
        print("✅ Upload avviato con successo!")
        print()
        print(json.dumps(result, indent=2))
        
        if 'name' in result:
            print()
            print(f"Operation Name: {result['name']}")
    else:
        print("❌ Errore durante upload!")
        print()
        print(f"Response Text: {response.text}")
        try:
            import json
            error_data = response.json()
            print()
            print("Error JSON:")
            print(json.dumps(error_data, indent=2))
        except:
            pass
            
except Exception as e:
    print(f"❌ Eccezione: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
