#!/usr/bin/env python3
"""
Script di setup per verificare la configurazione e avviare l'applicazione
"""
import os
import sys
from pathlib import Path

def check_python_version():
    """Verifica versione Python"""
    if sys.version_info < (3, 8):
        print("❌ Errore: Python 3.8 o superiore richiesto")
        print(f"   Versione corrente: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]}")
    return True

def check_env_file():
    """Verifica esistenza file .env"""
    if not Path('.env').exists():
        print("❌ File .env non trovato")
        print("   Crea il file .env copiando .env.example:")
        print("   Copy-Item .env.example .env")
        return False
    print("✅ File .env trovato")
    return True

def check_env_variables():
    """Verifica variabili d'ambiente"""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('GEMINI_API_KEY')
    store_name = os.getenv('FILE_SEARCH_STORE_NAME')
    
    errors = []
    
    if not api_key or api_key == 'your_api_key_here':
        errors.append("GEMINI_API_KEY non configurata correttamente")
    else:
        print("✅ GEMINI_API_KEY configurata")
    
    if not store_name or store_name == 'fileSearchStores/your-store-name':
        errors.append("FILE_SEARCH_STORE_NAME non configurato correttamente")
    else:
        print(f"✅ FILE_SEARCH_STORE_NAME: {store_name}")
    
    if errors:
        print("\n❌ Errori di configurazione:")
        for error in errors:
            print(f"   - {error}")
        return False
    
    return True

def check_dependencies():
    """Verifica dipendenze installate"""
    try:
        import flask
        import flask_cors
        import requests
        import dotenv
        print("✅ Tutte le dipendenze installate")
        return True
    except ImportError as e:
        print(f"❌ Dipendenza mancante: {e.name}")
        print("   Installa le dipendenze con:")
        print("   pip install -r requirements.txt")
        return False

def main():
    print("=" * 60)
    print("  Setup Gestione Documenti - Google RAG File Search")
    print("=" * 60)
    print()
    
    checks = [
        ("Versione Python", check_python_version),
        ("Dipendenze", check_dependencies),
        ("File .env", check_env_file),
        ("Variabili d'ambiente", check_env_variables),
    ]
    
    all_ok = True
    for name, check_func in checks:
        print(f"\n🔍 Verifica {name}...")
        if not check_func():
            all_ok = False
    
    print("\n" + "=" * 60)
    
    if all_ok:
        print("✅ Configurazione completata con successo!")
        print("\nPer avviare l'applicazione:")
        print("  cd backend")
        print("  python app.py")
        print("\nPoi apri il browser su: http://localhost:5000")
    else:
        print("❌ Configurazione incompleta. Risolvi gli errori sopra.")
        sys.exit(1)
    
    print("=" * 60)

if __name__ == '__main__':
    main()
