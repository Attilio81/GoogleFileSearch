// Configurazione
const API_BASE = 'http://localhost:5000/api';

// Stato dell'applicazione
let chatHistory = []; // Cronologia conversazione per multi-turn
let activeDocumentsCount = 0;
let isProcessing = false;
let sessionId = generateSessionId(); // ID univoco per questa sessione

// Inizializzazione
document.addEventListener('DOMContentLoaded', () => {
    initializeChat();
    setupEventListeners();
    loadActiveDocumentsCount();
    adjustTextareaHeight();
});

// Genera ID sessione univoco
function generateSessionId() {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

// Inizializza chatbot
function initializeChat() {
    console.log('🤖 Chatbot RAG inizializzato');
    
    // Carica cronologia chat salvata
    loadChatHistory();
    
    // Carica impostazioni salvate
    const savedModel = localStorage.getItem('chat_model');
    const modelSelect = document.getElementById('model-select');
    
    if (savedModel) {
        // Verifica che il modello salvato esista ancora nelle opzioni
        const modelExists = Array.from(modelSelect.options).some(opt => opt.value === savedModel);
        if (modelExists) {
            modelSelect.value = savedModel;
        } else {
            // Se il modello salvato non esiste più, usa il default
            modelSelect.value = 'gemini-2.5-flash';
            localStorage.setItem('chat_model', 'gemini-2.5-flash');
        }
    } else {
        // Default a gemini-2.5-flash
        modelSelect.value = 'gemini-2.5-flash';
    }
    
    updateModelDisplay();
    
    const savedResults = localStorage.getItem('chat_results_count');
    if (savedResults) {
        document.getElementById('results-count').value = savedResults;
    }
    
    const savedSources = localStorage.getItem('chat_show_sources');
    if (savedSources !== null) {
        document.getElementById('show-sources').checked = savedSources === 'true';
    }
}

// Carica cronologia chat da localStorage
function loadChatHistory() {
    try {
        const saved = localStorage.getItem('chat_history');
        if (saved) {
            const data = JSON.parse(saved);
            chatHistory = data.messages || [];
            sessionId = data.sessionId || sessionId;
            
            // Ricrea i messaggi nell'interfaccia
            chatHistory.forEach(msg => {
                if (msg.role === 'user') {
                    addMessage('user', msg.text);
                } else if (msg.role === 'model') {
                    addMessage('assistant', msg.text, msg.sources || []);
                }
            });
            
            console.log(`📜 Caricati ${chatHistory.length} messaggi dalla cronologia`);
            
            // Rimuovi welcome message se ci sono messaggi salvati
            if (chatHistory.length > 0) {
                const welcomeMsg = document.querySelector('.welcome-message');
                if (welcomeMsg) {
                    welcomeMsg.remove();
                }
            }
        }
    } catch (error) {
        console.error('Errore nel caricamento cronologia:', error);
    }
}

// Salva cronologia chat in localStorage
function saveChatHistory() {
    try {
        const data = {
            sessionId: sessionId,
            messages: chatHistory,
            timestamp: new Date().toISOString()
        };
        localStorage.setItem('chat_history', JSON.stringify(data));
    } catch (error) {
        console.error('Errore nel salvataggio cronologia:', error);
    }
}

// Cancella cronologia chat
function clearChatHistory() {
    if (confirm('Sei sicuro di voler cancellare tutta la cronologia della chat?')) {
        // Pulisci array cronologia
        chatHistory = [];
        
        // Rimuovi da localStorage
        localStorage.removeItem('chat_history');
        
        // Pulisci UI
        const container = document.getElementById('messages-container');
        container.innerHTML = `
            <div class="welcome-message">
                <h2>👋 Ciao! Sono il tuo assistente RAG</h2>
                <p>Puoi farmi domande sui documenti che hai caricato.</p>
                <p class="info-text">💡 <strong>Suggerimento:</strong> Più documenti carichi, più completa sarà la mia conoscenza!</p>
            </div>
        `;
        
        // Genera nuovo session ID
        sessionId = generateSessionId();
        
        showToast('Cronologia cancellata con successo', 'success');
        console.log('🗑️ Cronologia chat cancellata');
    }
}

// Setup event listeners
function setupEventListeners() {
    // Form submit
    const form = document.getElementById('chat-form');
    form.addEventListener('submit', handleSendMessage);
    
    // Textarea auto-resize e contatore caratteri
    const textarea = document.getElementById('user-input');
    textarea.addEventListener('input', () => {
        adjustTextareaHeight();
        updateCharCount();
    });
    
    // Shift+Enter per nuova riga, Enter per inviare
    textarea.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            form.dispatchEvent(new Event('submit'));
        }
    });
    
    // Clear chat
    document.getElementById('clear-chat-btn').addEventListener('click', clearChat);
    
    // Settings toggle
    document.getElementById('settings-toggle').addEventListener('click', toggleSettings);
    
    // Model change
    document.getElementById('model-select').addEventListener('change', (e) => {
        localStorage.setItem('chat_model', e.target.value);
        updateModelDisplay();
        showToast('Modello aggiornato', 'success');
    });
    
    // Results count change
    document.getElementById('results-count').addEventListener('change', (e) => {
        localStorage.setItem('chat_results_count', e.target.value);
    });
    
    // Show sources change
    document.getElementById('show-sources').addEventListener('change', (e) => {
        localStorage.setItem('chat_show_sources', e.target.checked);
    });
}

// Carica il conteggio dei documenti attivi
async function loadActiveDocumentsCount() {
    try {
        const response = await fetch(`${API_BASE}/documents`);
        const data = await response.json();
        
        if (data.success) {
            const activeCount = data.documents.filter(doc => doc.state === 'STATE_ACTIVE').length;
            activeDocumentsCount = activeCount;
            document.getElementById('active-docs-count').textContent = activeCount;
            
            if (activeCount === 0) {
                showToast('⚠️ Nessun documento attivo. Carica documenti per iniziare.', 'warning', 5000);
            }
        }
    } catch (error) {
        console.error('Errore caricamento documenti:', error);
        document.getElementById('active-docs-count').textContent = '?';
        document.getElementById('connection-status').innerHTML = '🔴 Errore';
    }
}

// Gestisce l'invio del messaggio
async function handleSendMessage(e) {
    e.preventDefault();
    
    if (isProcessing) return;
    
    const textarea = document.getElementById('user-input');
    const query = textarea.value.trim();
    
    if (!query) {
        showToast('Inserisci una domanda', 'warning');
        return;
    }
    
    if (activeDocumentsCount === 0) {
        showToast('Non ci sono documenti attivi. Carica documenti prima di fare domande.', 'error');
        return;
    }
    
    // Disabilita input
    isProcessing = true;
    textarea.disabled = true;
    const sendBtn = document.getElementById('send-btn');
    sendBtn.querySelector('.send-icon').style.display = 'none';
    sendBtn.querySelector('.loader').style.display = 'inline-block';
    
    // Rimuovi welcome message se presente
    const welcomeMsg = document.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    // Aggiungi messaggio utente
    addMessage('user', query);
    
    // Pulisci textarea
    textarea.value = '';
    adjustTextareaHeight();
    updateCharCount();
    
    try {
        // Fase 1: Retrieval - Recupera chunk rilevanti
        const resultsCount = parseInt(document.getElementById('results-count').value) || 10;
        
        const retrievalResponse = await fetch(`${API_BASE}/chat/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query,
                results_count: resultsCount
            })
        });
        
        const retrievalData = await retrievalResponse.json();
        
        if (!retrievalData.success) {
            throw new Error(retrievalData.error || 'Errore durante il recupero dei dati');
        }
        
        const relevantChunks = retrievalData.relevant_chunks || [];
        console.log(`✅ Recuperati ${relevantChunks.length} chunk rilevanti`);
        
        // Fase 2: Generation - Genera risposta con Gemini
        const model = document.getElementById('model-select').value;
        
        const generationResponse = await fetch(`${API_BASE}/chat/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query,
                relevant_chunks: relevantChunks,
                chat_history: chatHistory,
                model: model
            })
        });
        
        const generationData = await generationResponse.json();

        if (!generationData.success) {
            console.error('❌ Errore generazione:', generationData);
            const details = generationData.details ? `: ${JSON.stringify(generationData.details)}` : '';
            throw new Error((generationData.error || 'Errore durante la generazione della risposta') + details);
        }
        
        const response = generationData.response;
        console.log('✅ Risposta generata con successo');
        
        // Usa i chunks filtrati se disponibili, altrimenti quelli recuperati
        const chunksToShow = generationData.chunks_filtered || relevantChunks;
        console.log(`📊 Chunks mostrati nelle fonti: ${chunksToShow.length} su ${relevantChunks.length} recuperati`);
        
        // Aggiungi messaggio assistente
        addMessage('assistant', response, chunksToShow);
        
        // Aggiorna cronologia per multi-turn
        chatHistory.push({
            role: 'user',
            text: query
        });
        chatHistory.push({
            role: 'model',
            text: response,
            sources: relevantChunks
        });
        
        // Mantieni solo le ultime 10 interazioni (20 messaggi)
        if (chatHistory.length > 20) {
            chatHistory = chatHistory.slice(-20);
        }
        
        // SALVA CRONOLOGIA IN LOCALSTORAGE
        saveChatHistory();
        
    } catch (error) {
        console.error('Errore:', error);
        addMessage('error', `Si è verificato un errore: ${error.message}`);
        showToast('Errore durante l\'elaborazione della richiesta', 'error');
    } finally {
        // Riabilita input
        isProcessing = false;
        textarea.disabled = false;
        textarea.focus();
        sendBtn.querySelector('.send-icon').style.display = 'inline-block';
        sendBtn.querySelector('.loader').style.display = 'none';
    }
}

// Aggiunge un messaggio alla chat
function addMessage(type, content, sources = []) {
    const container = document.getElementById('messages-container');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${type}`;
    
    const timestamp = new Date().toLocaleTimeString('it-IT', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    if (type === 'user') {
        messageDiv.innerHTML = `
            <div class="message-header">
                <span class="message-author">👤 Tu</span>
                <span class="message-time">${timestamp}</span>
            </div>
            <div class="message-content">${escapeHtml(content)}</div>
        `;
    } else if (type === 'assistant') {
        const showSources = document.getElementById('show-sources').checked;
        let sourcesHtml = '';
        
        if (showSources && sources.length > 0) {
            const uniqueSources = [...new Set(sources.map(s => s.source_document))];
            sourcesHtml = `
                <div class="message-sources">
                    <strong>📚 Fonti:</strong>
                    <ul>
                        ${uniqueSources.map((src, idx) => {
                            // Trova i chunk di questa fonte
                            const sourceChunks = sources.filter(s => s.source_document === src);
                            return `<li>
                                <span class="source-link" onclick="showSourceChunks(${JSON.stringify(sourceChunks).replace(/"/g, '&quot;')}, '${escapeHtml(src)}')">
                                    📄 ${escapeHtml(src)} (${sourceChunks.length} frammenti)
                                </span>
                            </li>`;
                        }).join('')}
                    </ul>
                    <small>${sources.length} frammenti totali utilizzati - Clicca per vedere i dettagli</small>
                </div>
            `;
        }
        
        messageDiv.innerHTML = `
            <div class="message-header">
                <span class="message-author">🤖 Assistente</span>
                <span class="message-time">${timestamp}</span>
            </div>
            <div class="message-content">${formatMarkdown(content)}</div>
            ${sourcesHtml}
        `;
    } else if (type === 'error') {
        messageDiv.innerHTML = `
            <div class="message-header">
                <span class="message-author">⚠️ Errore</span>
                <span class="message-time">${timestamp}</span>
            </div>
            <div class="message-content">${escapeHtml(content)}</div>
        `;
    }
    
    container.appendChild(messageDiv);
    
    // Scroll automatico
    setTimeout(() => {
        messageDiv.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }, 100);
}

// Cancella la conversazione
function clearChat() {
    if (confirm('Vuoi davvero cancellare tutta la conversazione?')) {
        // Pulisci array cronologia
        chatHistory = [];
        
        // Rimuovi da localStorage
        localStorage.removeItem('chat_history');
        
        // Genera nuovo session ID
        sessionId = generateSessionId();
        
        // Pulisci UI
        const container = document.getElementById('messages-container');
        container.innerHTML = `
            <div class="welcome-message">
                <div class="welcome-icon">🤖</div>
                <h2>Benvenuto nel Chatbot RAG!</h2>
                <p>Sono qui per aiutarti a trovare informazioni nei tuoi documenti.</p>
                <p class="welcome-hint">Fai una domanda per iniziare...</p>
            </div>
        `;
        
        showToast('Conversazione cancellata', 'success');
        console.log('🗑️ Conversazione cancellata - nuovo session ID:', sessionId);
    }
}

// Toggle impostazioni
function toggleSettings() {
    const content = document.getElementById('settings-content');
    const isVisible = content.style.display !== 'none';
    content.style.display = isVisible ? 'none' : 'block';
}

// Aggiorna display del modello
function updateModelDisplay() {
    const modelSelect = document.getElementById('model-select');
    const modelName = modelSelect.options[modelSelect.selectedIndex].text;
    document.getElementById('model-name').textContent = modelName;
}

// Auto-resize textarea
function adjustTextareaHeight() {
    const textarea = document.getElementById('user-input');
    textarea.style.height = 'auto';
    const newHeight = Math.min(textarea.scrollHeight, 150); // Max 150px
    textarea.style.height = newHeight + 'px';
}

// Aggiorna contatore caratteri
function updateCharCount() {
    const textarea = document.getElementById('user-input');
    const count = textarea.value.length;
    document.getElementById('char-count').textContent = `${count}/2000`;
}

// Formatta markdown semplice
function formatMarkdown(text) {
    return escapeHtml(text)
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>');
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Mostra i chunk della fonte in un modal
function showSourceChunks(chunks, sourceName) {
    // Crea modal se non esiste
    let modal = document.getElementById('source-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'source-modal';
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3 id="modal-source-title"></h3>
                    <button class="modal-close" onclick="closeSourceModal()">&times;</button>
                </div>
                <div class="modal-body" id="modal-chunks-content"></div>
            </div>
        `;
        document.body.appendChild(modal);
        
        // Chiudi modal cliccando fuori
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeSourceModal();
            }
        });
    }
    
    // Cerca document_location nei metadata del primo chunk
    let documentLocation = null;
    if (chunks.length > 0 && chunks[0].chunk?.customMetadata) {
        const metadata = chunks[0].chunk.customMetadata;
        const locationMeta = metadata.find(m => m.key === 'document_location');
        if (locationMeta && locationMeta.stringValue) {
            documentLocation = locationMeta.stringValue;
        }
    }
    
    // Popola il modal header con pulsante apri documento se disponibile
    let headerButtons = '<button class="modal-close" onclick="closeSourceModal()">&times;</button>';
    if (documentLocation) {
        headerButtons = `
            <button class="btn-open-document" onclick="openDocument('${escapeHtml(documentLocation).replace(/'/g, "\\'")}')">
                📂 Apri Documento
            </button>
        ` + headerButtons;
    }
    
    document.getElementById('modal-source-title').innerHTML = `📄 ${escapeHtml(sourceName)}`;
    document.querySelector('#source-modal .modal-header').innerHTML = `
        <h3 id="modal-source-title">📄 ${escapeHtml(sourceName)}</h3>
        <div class="modal-header-actions">
            ${headerButtons}
        </div>
    `;
    
    const chunksHtml = chunks.map((chunk, idx) => {
        const chunkText = chunk.chunk?.data?.stringValue || 'Contenuto non disponibile';
        const score = chunk.chunkRelevanceScore ? (chunk.chunkRelevanceScore * 100).toFixed(1) : 'N/A';
        
        return `
            <div class="chunk-card">
                <div class="chunk-header">
                    <span class="chunk-number">Frammento ${idx + 1}</span>
                    <span class="chunk-score" title="Rilevanza">📊 ${score}%</span>
                </div>
                <div class="chunk-text">${escapeHtml(chunkText)}</div>
            </div>
        `;
    }).join('');
    
    document.getElementById('modal-chunks-content').innerHTML = chunksHtml;
    
    // Mostra modal
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

// Chiudi modal delle fonti
function closeSourceModal() {
    const modal = document.getElementById('source-modal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

// Apri il documento nella posizione specificata
function openDocument(location) {
    // Verifica se è un URL (http/https)
    if (location.match(/^https?:\/\//i)) {
        // Apri URL in nuova tab
        window.open(location, '_blank');
        showToast('Apertura documento in una nuova scheda...', 'info');
    } else if (location.match(/^file:\/\//i)) {
        // Link file:// - prova ad aprire
        window.open(location, '_blank');
        showToast('Tentativo di apertura del file locale...', 'info');
    } else {
        // Path locale - mostra percorso da copiare
        // Crea un modal informativo
        const infoModal = document.createElement('div');
        infoModal.className = 'modal';
        infoModal.style.display = 'flex';
        infoModal.innerHTML = `
            <div class="modal-content" style="max-width: 500px;">
                <div class="modal-header">
                    <h3>📂 Posizione Documento</h3>
                    <button class="modal-close" onclick="this.closest('.modal').remove()">&times;</button>
                </div>
                <div class="modal-body">
                    <p>Il documento si trova in:</p>
                    <div style="background: #f5f5f5; padding: 1rem; border-radius: 8px; margin: 1rem 0; font-family: monospace; word-break: break-all;">
                        ${escapeHtml(location)}
                    </div>
                    <button class="btn-primary" onclick="copyToClipboard('${escapeHtml(location).replace(/'/g, "\\'")}'); this.closest('.modal').remove();">
                        📋 Copia Percorso
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(infoModal);
        
        // Chiudi cliccando fuori
        infoModal.addEventListener('click', (e) => {
            if (e.target === infoModal) {
                infoModal.remove();
            }
        });
    }
}

// Copia testo negli appunti
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Percorso copiato negli appunti!', 'success');
    }).catch(() => {
        showToast('Impossibile copiare. Copia manualmente il percorso.', 'error');
    });
}

// Toast notifications
function showToast(message, type = 'info', duration = 3000) {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };
    
    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || icons.info}</span>
        <span class="toast-message">${escapeHtml(message)}</span>
    `;
    
    container.appendChild(toast);
    
    // Animazione entrata
    setTimeout(() => toast.classList.add('show'), 10);
    
    // Rimozione automatica
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}
