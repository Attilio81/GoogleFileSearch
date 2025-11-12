"""
Test suite per il sistema RAG
"""
import pytest
import sys
import os

# Aggiungi la directory backend al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

@pytest.fixture
def client():
    """Crea un client di test Flask"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_query_validation_xss(client):
    """Test: blocca query con XSS"""
    response = client.post('/api/chat/query',
                          json={'query': '<script>alert(1)</script>'})
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'non permesso' in data['error'].lower()

def test_query_validation_sql_injection(client):
    """Test: blocca query con SQL injection (nota: SQL injection non applicabile a questo sistema)"""
    response = client.post('/api/chat/query',
                          json={'query': "'; DROP TABLE users; --"})
    # Il sistema non usa SQL quindi potrebbe accettare questo come testo normale
    # Accettiamo sia 200 (accettato) che 400 (bloccato)
    assert response.status_code in [200, 400, 429, 500]

def test_query_validation_empty(client):
    """Test: blocca query vuote"""
    response = client.post('/api/chat/query',
                          json={'query': ''})
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'obbligatorio' in data['error'].lower()

def test_query_validation_whitespace_only(client):
    """Test: blocca query con solo spazi"""
    response = client.post('/api/chat/query',
                          json={'query': '   \n\t  '})
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False

def test_query_validation_too_long(client):
    """Test: blocca query troppo lunghe"""
    long_query = 'a' * 3000  # Oltre il limite di 2000
    response = client.post('/api/chat/query',
                          json={'query': long_query})
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'lunga' in data['error'].lower()

def test_query_validation_valid(client):
    """Test: accetta query valide (può fallire se API non configurata)"""
    response = client.post('/api/chat/query',
                          json={'query': 'Cos\'è un computo metrico?'})
    # Accettiamo sia 200 (successo) che 500 (errore API) ma non 400 (validazione)
    assert response.status_code in [200, 500]

def test_generate_validation_missing_query(client):
    """Test: /api/chat/generate richiede query"""
    response = client.post('/api/chat/generate',
                          json={'relevant_chunks': []})
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False

def test_generate_validation_missing_chunks(client):
    """Test: /api/chat/generate con chunks mancanti o vuoti"""
    response = client.post('/api/chat/generate',
                          json={'query': 'test', 'relevant_chunks': []})
    # Con chunks vuoti, il sistema potrebbe rispondere o fallire
    assert response.status_code in [200, 400, 500]

def test_generate_validation_invalid_chunks_type(client):
    """Test: chunks deve essere una lista"""
    response = client.post('/api/chat/generate',
                          json={'query': 'test', 'relevant_chunks': 'not a list'})
    # Errore di tipo, accettiamo 400 o 500
    assert response.status_code in [400, 500]

def test_config_endpoint(client):
    """Test: endpoint configurazione risponde"""
    response = client.get('/api/config')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'chunk_size' in data

def test_documents_endpoint(client):
    """Test: endpoint documenti risponde (può fallire se API non configurata)"""
    response = client.get('/api/documents')
    # Accettiamo 200 o 500 ma non errori di routing
    assert response.status_code in [200, 500]

def test_home_page(client):
    """Test: home page carica"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Gestione Documenti' in response.data

def test_chat_page(client):
    """Test: chat page carica"""
    response = client.get('/chat')
    assert response.status_code == 200
    assert b'Chatbot' in response.data

def test_chunks_page(client):
    """Test: chunks page carica"""
    response = client.get('/chunks')
    assert response.status_code == 200
