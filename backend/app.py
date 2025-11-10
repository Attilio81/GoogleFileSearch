from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
import logging
from werkzeug.utils import secure_filename
import mimetypes
import time

# Carica variabili d'ambiente
load_dotenv()

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
CORS(app)

# Configurazione
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
FILE_SEARCH_STORE_NAME = os.getenv('FILE_SEARCH_STORE_NAME')
BASE_URL = 'https://generativelanguage.googleapis.com/v1beta'
UPLOAD_BASE_URL = 'https://generativelanguage.googleapis.com/upload/v1beta'

# Dimensione massima file: 100MB
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

def get_headers():
    """Restituisce gli headers per le richieste API"""
    return {
        'x-goog-api-key': GEMINI_API_KEY
    }

def validate_config():
    """Valida la configurazione dell'applicazione"""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY non configurata")
    if not FILE_SEARCH_STORE_NAME:
        raise ValueError("FILE_SEARCH_STORE_NAME non configurato")
    logger.info(f"Configurazione valida. Store: {FILE_SEARCH_STORE_NAME}")

@app.route('/')
def index():
    """Pagina principale dell'interfaccia amministrativa"""
    return render_template('index.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    """Restituisce la configurazione corrente (senza API key)"""
    try:
        return jsonify({
            'success': True,
            'store_name': FILE_SEARCH_STORE_NAME,
            'api_configured': bool(GEMINI_API_KEY)
        })
    except Exception as e:
        logger.error(f"Errore nel recupero configurazione: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/documents', methods=['GET'])
def list_documents():
    """Elenca tutti i documenti nel File Search Store"""
    try:
        url = f"{BASE_URL}/{FILE_SEARCH_STORE_NAME}/documents"
        headers = get_headers()
        
        # Parametri opzionali per paginazione (max 20 per Google API)
        page_size = min(int(request.args.get('pageSize', 20)), 20)
        page_token = request.args.get('pageToken', '')
        
        params = {'pageSize': page_size}
        if page_token:
            params['pageToken'] = page_token
        
        logger.info(f"Recupero documenti da: {url}")
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        documents = data.get('documents', [])
        
        logger.info(f"Recuperati {len(documents)} documenti")
        
        return jsonify({
            'success': True,
            'documents': documents,
            'nextPageToken': data.get('nextPageToken', '')
        })
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Errore nella lista documenti: {str(e)}")
        error_detail = e.response.json() if hasattr(e, 'response') and e.response.content else str(e)
        return jsonify({
            'success': False,
            'error': 'Errore nel recupero dei documenti',
            'details': error_detail
        }), 500
    except Exception as e:
        logger.error(f"Errore imprevisto: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/documents/upload', methods=['POST'])
def upload_document():
    """Carica un documento nel File Search Store (Long-Running Operation)"""
    try:
        # Verifica presenza file
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'Nessun file fornito'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Nome file vuoto'}), 400
        
        # Recupera metadati opzionali
        display_name = request.form.get('displayName', file.filename)
        mime_type = request.form.get('mimeType', '')
        
        # Inferisci MIME type se non fornito
        if not mime_type:
            mime_type = mimetypes.guess_type(file.filename)[0] or 'application/octet-stream'
        
        # Metadati custom (opzionale)
        custom_metadata = {}
        metadata_keys = request.form.getlist('metadataKeys[]')
        metadata_values = request.form.getlist('metadataValues[]')
        for key, value in zip(metadata_keys, metadata_values):
            if key and value:
                custom_metadata[key] = value
        
        # URL per upload
        url = f"{UPLOAD_BASE_URL}/{FILE_SEARCH_STORE_NAME}:uploadToFileSearchStore"
        
        headers = get_headers()
        
        # Prepara i metadati del documento come JSON
        import json
        metadata = {
            'displayName': display_name[:512],  # Max 512 caratteri
            'mimeType': mime_type
        }
        
        if custom_metadata:
            metadata['customMetadata'] = [
                {'key': k, 'stringValue': v} for k, v in custom_metadata.items()
            ]
        
        # Prepara multipart upload con formato corretto per Google API
        # Deve avere esattamente 2 parti: metadata e file
        files = {
            'metadata': (None, json.dumps(metadata), 'application/json'),
            'file': (secure_filename(file.filename), file.stream, mime_type)
        }
        
        logger.info(f"Caricamento file: {file.filename} ({mime_type})")
        logger.info(f"Display name: {display_name}")
        logger.info(f"Metadata: {json.dumps(metadata)}")
        
        # Effettua l'upload - restituisce un'operazione
        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()
        
        operation_data = response.json()
        operation_name = operation_data.get('name', '')
        
        logger.info(f"Upload avviato. Operation: {operation_name}")
        
        return jsonify({
            'success': True,
            'operation': operation_data,
            'operationName': operation_name,
            'message': 'Upload avviato con successo. L\'elaborazione è in corso.'
        })
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Errore durante upload: {str(e)}")
        error_detail = e.response.json() if hasattr(e, 'response') and e.response.content else str(e)
        return jsonify({
            'success': False,
            'error': 'Errore durante il caricamento',
            'details': error_detail
        }), 500
    except Exception as e:
        logger.error(f"Errore imprevisto durante upload: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/operations/<path:operation_name>', methods=['GET'])
def get_operation_status(operation_name):
    """Recupera lo stato di un'operazione di upload"""
    try:
        # L'operation name è già completo (es: fileSearchStores/.../upload/operations/...)
        url = f"{BASE_URL}/{operation_name}"
        headers = get_headers()
        
        logger.info(f"Controllo stato operazione: {operation_name}")
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        operation_data = response.json()
        done = operation_data.get('done', False)
        
        result = {
            'success': True,
            'operation': operation_data,
            'done': done
        }
        
        if done:
            if 'error' in operation_data:
                result['error'] = operation_data['error']
                logger.warning(f"Operazione completata con errore: {operation_data['error']}")
            else:
                result['document'] = operation_data.get('response', {})
                logger.info(f"Operazione completata con successo")
        
        return jsonify(result)
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Errore nel controllo operazione: {str(e)}")
        error_detail = e.response.json() if hasattr(e, 'response') and e.response.content else str(e)
        return jsonify({
            'success': False,
            'error': 'Errore nel controllo dello stato',
            'details': error_detail
        }), 500
    except Exception as e:
        logger.error(f"Errore imprevisto: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/documents/<path:document_name>', methods=['DELETE'])
def delete_document(document_name):
    """Elimina un documento dal File Search Store"""
    try:
        # Il document_name include già il path completo (fileSearchStores/.../documents/...)
        url = f"{BASE_URL}/{document_name}"
        headers = get_headers()
        
        # IMPORTANTE: force=true elimina anche tutti i Chunk associati
        params = {'force': 'true'}
        
        logger.info(f"Eliminazione documento: {document_name}")
        
        response = requests.delete(url, headers=headers, params=params)
        response.raise_for_status()
        
        logger.info(f"Documento eliminato con successo")
        
        return jsonify({
            'success': True,
            'message': 'Documento eliminato con successo'
        })
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Errore durante eliminazione: {str(e)}")
        error_detail = e.response.json() if hasattr(e, 'response') and e.response.content else str(e)
        return jsonify({
            'success': False,
            'error': 'Errore durante l\'eliminazione',
            'details': error_detail
        }), 500
    except Exception as e:
        logger.error(f"Errore imprevisto: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== CHATBOT ENDPOINTS ====================

@app.route('/api/chat/query', methods=['POST'])
def query_documents():
    """
    Endpoint per eseguire una query sui documenti (Retrieval Phase)
    Recupera i chunk rilevanti dai documenti attivi
    """
    try:
        data = request.json
        query_text = data.get('query')
        document_name = data.get('document_name')  # Opzionale: nome specifico del documento
        results_count = data.get('results_count', 10)  # Default 10, max 100
        
        if not query_text:
            return jsonify({
                'success': False,
                'error': 'Query text è obbligatorio'
            }), 400
        
        logger.info(f"Query ricevuta: {query_text}")
        
        # Se non è specificato un documento, cerchiamo in tutti i documenti attivi
        if not document_name:
            # Prima otteniamo la lista dei documenti attivi
            list_url = f"{BASE_URL}/{FILE_SEARCH_STORE_NAME}/documents"
            list_response = requests.get(list_url, headers=get_headers())
            list_response.raise_for_status()
            
            documents_data = list_response.json()
            documents = documents_data.get('documents', [])
            
            # Filtra solo documenti attivi
            active_documents = [doc for doc in documents if doc.get('state') == 'STATE_ACTIVE']
            
            if not active_documents:
                return jsonify({
                    'success': False,
                    'error': 'Nessun documento attivo trovato'
                }), 404
            
            # Interroga tutti i documenti attivi e aggrega i risultati
            all_chunks = []
            for doc in active_documents:
                doc_name = doc.get('name')
                query_url = f"{BASE_URL}/{doc_name}:query"
                
                query_payload = {
                    'query': query_text,
                    'resultsCount': results_count
                }
                
                try:
                    query_response = requests.post(query_url, headers=get_headers(), json=query_payload)
                    query_response.raise_for_status()
                    
                    result = query_response.json()
                    chunks = result.get('relevantChunks', [])
                    
                    # Aggiungi informazioni sul documento sorgente
                    for chunk in chunks:
                        chunk['source_document'] = doc.get('displayName', doc_name)
                    
                    all_chunks.extend(chunks)
                except Exception as e:
                    logger.warning(f"Errore query su documento {doc_name}: {str(e)}")
                    continue
            
            # Ordina per rilevanza (assumendo che abbiano un campo score)
            all_chunks.sort(key=lambda x: x.get('chunkRelevanceScore', 0), reverse=True)
            
            # Limita al numero richiesto
            all_chunks = all_chunks[:results_count]
            
            return jsonify({
                'success': True,
                'relevant_chunks': all_chunks,
                'query': query_text,
                'documents_searched': len(active_documents)
            })
        
        else:
            # Query su un documento specifico
            query_url = f"{BASE_URL}/{document_name}:query"
            
            query_payload = {
                'query': query_text,
                'resultsCount': results_count
            }
            
            query_response = requests.post(query_url, headers=get_headers(), json=query_payload)
            query_response.raise_for_status()
            
            result = query_response.json()
            
            return jsonify({
                'success': True,
                'relevant_chunks': result.get('relevantChunks', []),
                'query': query_text
            })
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Errore durante query: {str(e)}")
        error_detail = e.response.json() if hasattr(e, 'response') and e.response.content else str(e)
        return jsonify({
            'success': False,
            'error': 'Errore durante la query',
            'details': error_detail
        }), 500
    except Exception as e:
        logger.error(f"Errore imprevisto: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/chat/generate', methods=['POST'])
def generate_response():
    """
    Endpoint per generare una risposta usando Gemini (Generation Phase)
    Prende i chunk rilevanti e genera una risposta coerente
    """
    try:
        data = request.json
        query_text = data.get('query')
        relevant_chunks = data.get('relevant_chunks', [])
        chat_history = data.get('chat_history', [])  # Per conversazioni multi-turn
        model = data.get('model', 'gemini-2.5-flash-lite')  # Default model
        
        if not query_text:
            return jsonify({
                'success': False,
                'error': 'Query text è obbligatorio'
            }), 400
        
        logger.info(f"Generazione risposta per: {query_text}")
        
        # Costruisci il contesto dai chunk rilevanti
        context_parts = []
        if relevant_chunks:
            context_parts.append("Utilizza ESCLUSIVAMENTE i seguenti frammenti di contesto per rispondere alla domanda dell'utente:\n\n")
            for i, chunk in enumerate(relevant_chunks, 1):
                chunk_text = chunk.get('chunk', {}).get('data', {}).get('stringValue', '')
                source = chunk.get('source_document', 'documento')
                context_parts.append(f"[Frammento {i} da {source}]:\n{chunk_text}\n\n")
        
        # Costruisci l'array contents per la conversazione
        contents = []
        
        # Aggiungi la cronologia della chat se presente
        for message in chat_history:
            contents.append({
                'role': message.get('role'),
                'parts': [{'text': message.get('text')}]
            })
        
        # Costruisci il prompt finale per l'utente
        user_prompt = ''.join(context_parts) if context_parts else ''
        user_prompt += f"\n\nDomanda: {query_text}"
        
        if context_parts:
            user_prompt += "\n\nSe la risposta non può essere trovata nel contesto fornito, dillo chiaramente."
        
        contents.append({
            'role': 'user',
            'parts': [{'text': user_prompt}]
        })
        
        # Chiamata all'API Gemini
        generate_url = f"{BASE_URL}/models/{model}:generateContent"
        
        payload = {
            'contents': contents,
            'generationConfig': {
                'temperature': 0.7,
                'topK': 40,
                'topP': 0.95,
                'maxOutputTokens': 2048,
            }
        }
        
        # Esegui la chiamata al modello con retries su 429 (rate limit)
        max_retries = 3
        delay = 1
        response = None
        for attempt in range(max_retries):
            try:
                response = requests.post(generate_url, headers=get_headers(), json=payload, timeout=60)
                response.raise_for_status()
                break
            except requests.exceptions.HTTPError as he:
                status = he.response.status_code if he.response is not None else None
                # Se riceviamo 429 (Too Many Requests), ritentiamo con backoff
                if status == 429 and attempt < max_retries - 1:
                    logger.warning(f"429 from Gemini API, retry {attempt+1}/{max_retries} after {delay}s")
                    time.sleep(delay)
                    delay *= 2
                    continue
                # Non gestito qui: rilancia per essere catturato più in basso
                raise
        
        if response is None:
            raise RuntimeError('Nessuna risposta dal servizio di generazione')

        result = response.json()
        
        # Estrai il testo della risposta
        candidates = result.get('candidates', [])
        if not candidates:
            return jsonify({
                'success': False,
                'error': 'Nessuna risposta generata dal modello'
            }), 500
        
        response_text = candidates[0].get('content', {}).get('parts', [{}])[0].get('text', '')
        
        return jsonify({
            'success': True,
            'response': response_text,
            'query': query_text,
            'model': model,
            'chunks_used': len(relevant_chunks)
        })
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Errore durante generazione: {str(e)}")
        # Se l'errore proviene dall'API esterna, proviamo ad estrarre lo status code
        status_code = None
        try:
            status_code = e.response.status_code
        except Exception:
            status_code = None

        error_detail = None
        try:
            error_detail = e.response.json() if hasattr(e, 'response') and e.response.content else str(e)
        except Exception:
            error_detail = str(e)

        # Se l'API esterna ha restituito 429 (rate limit), inoltriamo 429 al client con dettagli
        if status_code == 429:
            return jsonify({
                'success': False,
                'error': 'Rate limit raggiunto presso il servizio di generazione (429)',
                'details': error_detail
            }), 429

        return jsonify({
            'success': False,
            'error': 'Errore durante la generazione della risposta',
            'details': error_detail
        }), 500
    except Exception as e:
        logger.error(f"Errore imprevisto: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/chat')
def chat_page():
    """Pagina dell'interfaccia chatbot"""
    return render_template('chat.html')

@app.errorhandler(413)
def request_entity_too_large(error):
    """Gestisce errori di file troppo grandi"""
    return jsonify({
        'success': False,
        'error': 'File troppo grande. Dimensione massima: 100MB'
    }), 413

@app.errorhandler(500)
def internal_error(error):
    """Gestisce errori interni del server"""
    logger.error(f"Errore interno del server: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'Errore interno del server'
    }), 500

if __name__ == '__main__':
    try:
        validate_config()
        logger.info("Avvio server Flask...")
        # Disabilito use_reloader per evitare problemi con watchdog su Windows
        app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
    except ValueError as e:
        logger.error(f"Errore di configurazione: {str(e)}")
        print(f"\n❌ ERRORE: {str(e)}")
        print("Assicurati di aver configurato correttamente il file .env")
