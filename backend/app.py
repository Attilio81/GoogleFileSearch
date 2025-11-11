from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
import logging
from werkzeug.utils import secure_filename
import mimetypes
import time
import tempfile
import json
from datetime import datetime, timedelta
from typing import Dict, Optional

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
DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'gemini-2.5-pro')
DEFAULT_CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '512'))
CHUNK_OVERLAP_PERCENT = int(os.getenv('CHUNK_OVERLAP_PERCENT', '10'))
RESULTS_COUNT = int(os.getenv('RESULTS_COUNT', '25'))
MIN_RELEVANCE_SCORE = float(os.getenv('MIN_RELEVANCE_SCORE', '0.3'))
MAX_CHUNKS_FOR_GENERATION = int(os.getenv('MAX_CHUNKS_FOR_GENERATION', '15'))
BASE_URL = 'https://generativelanguage.googleapis.com/v1beta'
UPLOAD_BASE_URL = 'https://generativelanguage.googleapis.com/upload/v1beta'

# Dimensione massima file: 100MB
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
# Upload folder temporaneo
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
# Cartella per archiviare i documenti caricati (per download futuro)
app.config['DOCUMENTS_STORAGE'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'documents_storage')
# Crea la cartella se non esiste
os.makedirs(app.config['DOCUMENTS_STORAGE'], exist_ok=True)

# MIME types permessi
ALLOWED_MIME_TYPES = {
    'application/pdf', 'text/plain', 'text/html', 'text/markdown',
    'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'text/csv', 'application/json'
}

# Circuit Breaker per gestione rate limit
class CircuitBreaker:
    """Circuit breaker per gestire rate limit 429"""
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout  # secondi
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def call_allowed(self) -> bool:
        """Verifica se la chiamata è permessa"""
        if self.state == 'CLOSED':
            return True
        
        if self.state == 'OPEN':
            # Verifica se è passato il timeout
            if self.last_failure_time and datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout):
                self.state = 'HALF_OPEN'
                logger.info("Circuit breaker: OPEN -> HALF_OPEN (timeout scaduto)")
                return True
            return False
        
        # HALF_OPEN: permette una chiamata di test
        return True
    
    def record_success(self):
        """Registra una chiamata riuscita"""
        self.failure_count = 0
        if self.state == 'HALF_OPEN':
            self.state = 'CLOSED'
            logger.info("Circuit breaker: HALF_OPEN -> CLOSED (successo)")
    
    def record_failure(self):
        """Registra una chiamata fallita"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
            logger.warning(f"Circuit breaker: OPEN (troppi errori: {self.failure_count})")

# Istanza globale del circuit breaker
gemini_circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60)

def get_headers():
    """Restituisce gli headers per le richieste API"""
    return {
        'x-goog-api-key': GEMINI_API_KEY
    }

def validate_query_text(query: str) -> tuple[bool, Optional[str]]:
    """
    Valida il testo della query
    Returns: (is_valid, error_message)
    """
    if not query or not query.strip():
        return False, "Query vuota"
    
    if len(query) > 2000:
        return False, "Query troppo lunga (max 2000 caratteri)"
    
    # Controllo caratteri pericolosi per injection
    dangerous_chars = ['<script', 'javascript:', 'onerror=', 'onclick=']
    query_lower = query.lower()
    for char in dangerous_chars:
        if char in query_lower:
            return False, f"Query contiene contenuto non permesso: {char}"
    
    return True, None

def validate_mime_type(mime_type: str, filename: str) -> tuple[bool, Optional[str]]:
    """
    Valida il MIME type del file
    Returns: (is_valid, error_message)
    """
    if not mime_type:
        # Inferisci dal filename
        mime_type, _ = mimetypes.guess_type(filename)
    
    if not mime_type:
        return False, "Impossibile determinare il tipo di file"
    
    if mime_type not in ALLOWED_MIME_TYPES:
        return False, f"Tipo di file non permesso: {mime_type}. Permessi: {', '.join(ALLOWED_MIME_TYPES)}"
    
    return True, None

def validate_metadata(metadata_keys: list, metadata_values: list) -> tuple[bool, Optional[str]]:
    """
    Valida i metadati custom (ignora righe vuote)
    Returns: (is_valid, error_message)
    """
    if len(metadata_keys) != len(metadata_values):
        return False, "Numero di chiavi e valori metadati non corrispondono"
    
    # Filtra solo metadati non vuoti per la validazione
    non_empty_pairs = [(k, v) for k, v in zip(metadata_keys, metadata_values) if k.strip() or v.strip()]
    
    if len(non_empty_pairs) > 50:
        return False, "Troppi metadati (max 50)"
    
    for key, value in non_empty_pairs:
        # Ignora coppie completamente vuote
        if not key.strip() and not value.strip():
            continue
            
        # Se la chiave è vuota ma il valore no, errore
        if not key.strip() and value.strip():
            return False, "Valore metadato senza chiave associata"
        
        # Valida lunghezza chiave
        if len(key) > 100:
            return False, f"Chiave metadato troppo lunga (max 100 caratteri): {key[:20]}..."
        
        # Controllo caratteri pericolosi nella chiave
        if any(c in key for c in ['<', '>', '"', "'", ';', '\n', '\r']):
            return False, f"Chiave metadato contiene caratteri non permessi: {key}"
        
        # Valida lunghezza valore
        if len(value) > 500:
            return False, f"Valore metadato troppo lungo (max 500 caratteri)"
    
    return True, None

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
            'api_configured': bool(GEMINI_API_KEY),
            'chunk_size': DEFAULT_CHUNK_SIZE,
            'chunk_overlap_percent': CHUNK_OVERLAP_PERCENT,
            'results_count': RESULTS_COUNT,
            'min_relevance_score': MIN_RELEVANCE_SCORE,
            'max_chunks_for_generation': MAX_CHUNKS_FOR_GENERATION
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
    temp_file_path = None
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
        chunk_size = int(request.form.get('chunkSize', DEFAULT_CHUNK_SIZE))  # Default dal .env
        
        # VALIDAZIONE CHUNK SIZE (limite API Google: 1-512)
        if chunk_size < 1 or chunk_size > 512:
            return jsonify({'success': False, 'error': f'Chunk size deve essere tra 1 e 512 (ricevuto: {chunk_size})'}), 400
        
        # Inferisci MIME type se non fornito
        if not mime_type:
            mime_type = mimetypes.guess_type(file.filename)[0] or 'application/octet-stream'
        
        # VALIDAZIONE MIME TYPE
        is_valid, error = validate_mime_type(mime_type, file.filename)
        if not is_valid:
            return jsonify({'success': False, 'error': error}), 400
        
        # Metadati custom (opzionale)
        custom_metadata = {}
        metadata_keys = request.form.getlist('metadataKeys[]')
        metadata_values = request.form.getlist('metadataValues[]')
        
        logger.info(f"Metadati ricevuti - Keys: {metadata_keys}, Values: {metadata_values}")
        
        # VALIDAZIONE METADATI
        if metadata_keys or metadata_values:
            is_valid, error = validate_metadata(metadata_keys, metadata_values)
            if not is_valid:
                logger.error(f"Validazione metadati fallita: {error}")
                return jsonify({'success': False, 'error': error}), 400
        
        # Filtra e aggiungi solo metadati non vuoti
        for key, value in zip(metadata_keys, metadata_values):
            if key and key.strip() and value and value.strip():
                custom_metadata[key.strip()] = value.strip()
        
        logger.info(f"Metadati custom validati: {custom_metadata}")
        
        # SALVA FILE TEMPORANEAMENTE SU DISCO (non in memoria)
        temp_file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"upload_{int(time.time())}_{secure_filename(file.filename)}")
        file.save(temp_file_path)
        logger.info(f"File salvato temporaneamente: {temp_file_path}")
        
        # URL per upload
        url = f"{UPLOAD_BASE_URL}/{FILE_SEARCH_STORE_NAME}:uploadToFileSearchStore"
        
        headers = get_headers()
        
        # Prepara i metadati del documento come JSON
        metadata = {
            'displayName': display_name.strip()[:100],  # Max 100 caratteri e senza spazi extra
            'mimeType': mime_type
        }
        
        if custom_metadata:
            metadata['customMetadata'] = [
                {'key': k, 'stringValue': v} for k, v in custom_metadata.items()
            ]
        
        # CONFIGURAZIONE CHUNKING per divisione ottimale del documento
        # La configurazione segue la struttura corretta dell'API Google
        chunk_overlap = min(int(chunk_size * CHUNK_OVERLAP_PERCENT / 100), 100)  # Overlap dal .env, max 100
        
        metadata['chunkingConfig'] = {
            'whiteSpaceConfig': {
                'maxTokensPerChunk': chunk_size,      # Dimensione massima chunk in token
                'maxOverlapTokens': chunk_overlap     # Token di sovrapposizione tra chunks
            }
        }
        
        logger.info(f"Chunking config: max_tokens={chunk_size}, overlap={chunk_overlap}")
        
        # Apri il file salvato e invialo (non usare stream che carica in memoria)
        with open(temp_file_path, 'rb') as f:
            files = {
                'metadata': (None, json.dumps(metadata), 'application/json'),
                'file': (secure_filename(file.filename), f, mime_type)
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
        error_detail = str(e)
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                logger.error(f"Dettagli errore API: {error_detail}")
            except:
                error_detail = e.response.text
                logger.error(f"Risposta errore API (testo): {error_detail}")
        return jsonify({
            'success': False,
            'error': 'Errore durante il caricamento',
            'details': error_detail
        }), 500
    except Exception as e:
        logger.error(f"Errore imprevisto durante upload: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        # PULIZIA FILE TEMPORANEO (anche se ci sono stati errori)
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                logger.info(f"File temporaneo eliminato: {temp_file_path}")
            except Exception as cleanup_error:
                logger.warning(f"Errore nella pulizia del file temporaneo: {cleanup_error}")

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
        results_count = data.get('results_count', RESULTS_COUNT)  # Default da .env, max 100
        
        if not query_text:
            return jsonify({
                'success': False,
                'error': 'Query text è obbligatorio'
            }), 400
        
        # VALIDAZIONE INPUT
        is_valid, error = validate_query_text(query_text)
        if not is_valid:
            return jsonify({'success': False, 'error': error}), 400
        
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
        model = data.get('model', DEFAULT_MODEL)  # Default dal .env
        
        if not query_text:
            return jsonify({
                'success': False,
                'error': 'Query text è obbligatorio'
            }), 400
        
        # VALIDAZIONE INPUT
        is_valid, error = validate_query_text(query_text)
        if not is_valid:
            return jsonify({'success': False, 'error': error}), 400
        
        # CONTROLLO CIRCUIT BREAKER
        if not gemini_circuit_breaker.call_allowed():
            logger.warning("Circuit breaker APERTO - troppe richieste fallite a Gemini API")
            return jsonify({
                'success': False,
                'error': 'Servizio temporaneamente non disponibile. Riprova tra qualche minuto.',
                'circuit_breaker_status': 'OPEN'
            }), 503
        
        logger.info(f"Generazione risposta per: {query_text}")
        
        # Filtra chunk per generazione basandoci sulla rilevanza
        # Usa solo chunk con score alto o limita il numero
        high_score_chunks = [
            chunk for chunk in relevant_chunks 
            if chunk.get('chunkRelevanceScore', 0) >= MIN_RELEVANCE_SCORE
        ]
        
        # Se abbiamo troppi chunk anche dopo il filtro, prendi i top N
        chunks_to_use = high_score_chunks[:MAX_CHUNKS_FOR_GENERATION]
        
        logger.info(f"Chunk recuperati: {len(relevant_chunks)}, Score >= {MIN_RELEVANCE_SCORE}: {len(high_score_chunks)}, Usati per generazione: {len(chunks_to_use)}")
        
        # Costruisci il contesto dai chunk rilevanti
        context_parts = []
        if chunks_to_use:
            context_parts.append("CONTESTO DOCUMENTI:\n\n")
            for i, chunk in enumerate(chunks_to_use, 1):
                chunk_text = chunk.get('chunk', {}).get('data', {}).get('stringValue', '')
                source = chunk.get('source_document', 'documento')
                context_parts.append(f"[Frammento {i} da {source}]:\n{chunk_text}\n\n")
        
        # Costruisci l'array contents per la conversazione
        contents = []
        
        # Aggiungi system instruction come primo messaggio user
        system_instruction = """Sei un assistente AI specializzato nel rispondere a domande basandoti ESCLUSIVAMENTE sui documenti forniti.

ISTRUZIONI IMPORTANTI:
1. Leggi attentamente la domanda dell'utente
2. Analizza i frammenti di contesto forniti
3. Rispondi SOLO alle informazioni specificamente richieste
4. Sintetizza e organizza la risposta in modo chiaro e conciso
5. Non copiare/incollare interi frammenti, ma estrai solo le info rilevanti
6. Se la risposta richiede dati da più frammenti, uniscili in modo coerente
7. Se l'informazione non è presente nel contesto, dillo chiaramente
8. Usa un linguaggio professionale ma comprensibile
9. Se appropriato, usa elenchi puntati per maggiore chiarezza"""
        
        # Aggiungi la cronologia della chat se presente
        for message in chat_history:
            contents.append({
                'role': message.get('role'),
                'parts': [{'text': message.get('text')}]
            })
        
        # Costruisci il prompt finale per l'utente
        if not chat_history:  # Solo al primo messaggio
            user_prompt = system_instruction + "\n\n" + ''.join(context_parts)
        else:
            user_prompt = ''.join(context_parts) if context_parts else ''
        
        user_prompt += f"\n\nDOMANDA UTENTE: {query_text}\n\nRISPOSTA:"
        
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
                
                # REGISTRA SUCCESSO NEL CIRCUIT BREAKER
                gemini_circuit_breaker.record_success()
                break
            except requests.exceptions.HTTPError as he:
                status = he.response.status_code if he.response is not None else None
                # Se riceviamo 429 (Too Many Requests), ritentiamo con backoff
                if status == 429:
                    # REGISTRA FALLIMENTO NEL CIRCUIT BREAKER
                    gemini_circuit_breaker.record_failure()
                    
                    if attempt < max_retries - 1:
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

@app.route('/api/chat/generate-stream', methods=['POST'])
def generate_response_stream():
    """
    Endpoint per generare una risposta in streaming usando Gemini
    Invia i chunk di testo man mano che vengono generati (SSE)
    """
    data = request.json
    query_text = data.get('query')
    relevant_chunks = data.get('relevant_chunks', [])
    chat_history = data.get('chat_history', [])
    model = data.get('model', DEFAULT_MODEL)  # Default dal .env
    
    # Validazione input
    if not query_text:
        return jsonify({'success': False, 'error': 'Query text è obbligatorio'}), 400
    
    is_valid, error = validate_query_text(query_text)
    if not is_valid:
        return jsonify({'success': False, 'error': error}), 400
    
    # Controllo circuit breaker
    if not gemini_circuit_breaker.call_allowed():
        return jsonify({
            'success': False,
            'error': 'Servizio temporaneamente non disponibile. Riprova tra qualche minuto.',
            'circuit_breaker_status': 'OPEN'
        }), 503
    
    def generate():
        """Generatore per lo streaming SSE"""
        try:
            # Filtra chunk per generazione basandoci sulla rilevanza
            high_score_chunks = [
                chunk for chunk in relevant_chunks 
                if chunk.get('chunkRelevanceScore', 0) >= MIN_RELEVANCE_SCORE
            ]
            
            chunks_to_use = high_score_chunks[:MAX_CHUNKS_FOR_GENERATION]
            
            logger.info(f"Streaming - Chunk recuperati: {len(relevant_chunks)}, Score >= {MIN_RELEVANCE_SCORE}: {len(high_score_chunks)}, Usati: {len(chunks_to_use)}")
            
            # Costruisci il contesto
            context_parts = []
            if chunks_to_use:
                context_parts.append("CONTESTO DOCUMENTI:\n\n")
                for i, chunk in enumerate(chunks_to_use, 1):
                    chunk_text = chunk.get('chunk', {}).get('data', {}).get('stringValue', '')
                    source = chunk.get('source_document', 'documento')
                    context_parts.append(f"[Frammento {i} da {source}]:\n{chunk_text}\n\n")
            
            # System instruction
            system_instruction = """Sei un assistente AI specializzato nel rispondere a domande basandoti ESCLUSIVAMENTE sui documenti forniti.

ISTRUZIONI IMPORTANTI:
1. Leggi attentamente la domanda dell'utente
2. Analizza i frammenti di contesto forniti
3. Rispondi SOLO alle informazioni specificamente richieste
4. Sintetizza e organizza la risposta in modo chiaro e conciso
5. Non copiare/incollare interi frammenti, ma estrai solo le info rilevanti
6. Se la risposta richiede dati da più frammenti, uniscili in modo coerente
7. Se l'informazione non è presente nel contesto, dillo chiaramente
8. Usa un linguaggio professionale ma comprensibile
9. Se appropriato, usa elenchi puntati per maggiore chiarezza"""
            
            # Costruisci contents
            contents = []
            for message in chat_history:
                contents.append({
                    'role': message.get('role'),
                    'parts': [{'text': message.get('text')}]
                })
            
            # Costruisci prompt
            if not chat_history:  # Solo al primo messaggio
                user_prompt = system_instruction + "\n\n" + ''.join(context_parts)
            else:
                user_prompt = ''.join(context_parts) if context_parts else ''
            
            user_prompt += f"\n\nDOMANDA UTENTE: {query_text}\n\nRISPOSTA:"
            
            contents.append({
                'role': 'user',
                'parts': [{'text': user_prompt}]
            })
            
            # Chiamata streaming all'API Gemini
            stream_url = f"{BASE_URL}/models/{model}:streamGenerateContent"
            payload = {
                'contents': contents,
                'generationConfig': {
                    'temperature': 0.7,
                    'topK': 40,
                    'topP': 0.95,
                    'maxOutputTokens': 2048,
                }
            }
            
            # Stream con requests
            with requests.post(stream_url, headers=get_headers(), json=payload, stream=True, timeout=60) as response:
                response.raise_for_status()
                gemini_circuit_breaker.record_success()
                
                # Gemini restituisce SSE con formato: data: {...}\n\n
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        # Rimuovi il prefisso "data: " se presente
                        if line_str.startswith('data: '):
                            line_str = line_str[6:]
                        
                        try:
                            chunk_data = json.loads(line_str)
                            candidates = chunk_data.get('candidates', [])
                            if candidates:
                                text_chunk = candidates[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                                if text_chunk:
                                    # Invia il chunk come SSE
                                    yield f"data: {json.dumps({'text': text_chunk})}\n\n"
                        except json.JSONDecodeError:
                            continue
                
                # Segnala fine dello streaming
                yield f"data: {json.dumps({'done': True})}\n\n"
                
        except requests.exceptions.HTTPError as he:
            if he.response and he.response.status_code == 429:
                gemini_circuit_breaker.record_failure()
            yield f"data: {json.dumps({'error': 'Errore durante la generazione'})}\n\n"
        except Exception as e:
            logger.error(f"Errore streaming: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@app.route('/chat')
def chat_page():
    """Pagina dell'interfaccia chatbot"""
    return render_template('chat.html')

@app.route('/chunks')
def chunks_page():
    """Pagina per visualizzare i chunks dei documenti"""
    return render_template('chunks.html')

@app.route('/api/documents/<path:document_name>/chunks', methods=['POST'])
def get_document_chunks(document_name):
    """
    Recupera tutti i chunks di un documento specifico tramite query.
    L'API Google non ha un endpoint diretto per listare chunks,
    quindi usiamo il metodo query con una stringa generica.
    
    Body params:
    - query: stringa di ricerca (opzionale, default: "*" per tutti i chunks)
    - resultsCount: numero di chunks da recuperare (max 100)
    """
    try:
        data = request.get_json() or {}
        query_string = data.get('query', '*')  # Query generica per ottenere tutti i chunks
        results_count = min(int(data.get('resultsCount', 100)), 100)  # Max 100 per API
        
        # Costruisci URL per query sui chunks del documento
        url = f"{BASE_URL}/{document_name}:query"
        
        headers = get_headers()
        headers['Content-Type'] = 'application/json'
        
        # Payload per la query
        payload = {
            'query': query_string,
            'resultsCount': results_count
        }
        
        logger.info(f"Query chunks su documento: {document_name}")
        logger.info(f"Query: '{query_string}', Max results: {results_count}")
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        response_data = response.json()
        relevant_chunks = response_data.get('relevantChunks', [])
        
        logger.info(f"Recuperati {len(relevant_chunks)} chunks")
        
        # Formatta i chunks per la visualizzazione
        formatted_chunks = []
        for idx, chunk_wrapper in enumerate(relevant_chunks):
            chunk = chunk_wrapper.get('chunk', {})
            chunk_data = chunk.get('data', {})
            
            formatted_chunks.append({
                'name': chunk.get('name', ''),
                'index': idx + 1,
                'stringValue': chunk_data.get('stringValue', ''),
                'state': chunk.get('state', 'STATE_ACTIVE'),
                'createTime': chunk.get('createTime', ''),
                'updateTime': chunk.get('updateTime', ''),
                'relevanceScore': chunk_wrapper.get('chunkRelevanceScore', 0)
            })
        
        return jsonify({
            'success': True,
            'chunks': formatted_chunks,
            'totalCount': len(formatted_chunks),
            'note': 'I chunks sono ordinati per rilevanza. Per vedere tutti i chunks, usa query generiche come "*" o "document".'
        })
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Errore durante recupero chunks: {e}")
        error_detail = {}
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
            except:
                error_detail = {'error': str(e)}
        logger.error(f"Dettagli errore API: {error_detail}")
        return jsonify({
            'success': False,
            'error': f'Errore nel recupero dei chunks: {str(e)}',
            'details': error_detail
        }), 500
    except Exception as e:
        logger.error(f"Errore imprevisto: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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
