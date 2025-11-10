// Configurazione
const API_BASE = 'http://localhost:5000/api';

// Stato dell'applicazione
let chatHistory = []; // Cronologia conversazione per multi-turn
let activeDocumentsCount = 0;
let isProcessing = false;

// Inizializzazione
document.addEventListener('DOMContentLoaded', () => {
    initializeChat();
    setupEventListeners();
    loadActiveDocumentsCount();
    adjustTextareaHeight();
});

// Inizializza chatbot
function initializeChat() {
    console.log('🤖 Chatbot RAG inizializzato');
    
    // Carica impostazioni salvate
    const savedModel = localStorage.getItem('chat_model');
    if (savedModel) {
        document.getElementById('model-select').value = savedModel;
        updateModelDisplay();
    } else {
        // Default a gemini-2.5-flash-lite
        document.getElementById('model-select').value = 'gemini-2.5-flash-lite';
        updateModelDisplay();
    }
    
    const savedResults = localStorage.getItem('chat_results_count');
    if (savedResults) {
        document.getElementById('results-count').value = savedResults;
    }
    
    const savedSources = localStorage.getItem('chat_show_sources');
    if (savedSources !== null) {
        document.getElementById('show-sources').checked = savedSources === 'true';
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
            const details = generationData.details ? `: ${generationData.details}` : '';
            throw new Error((generationData.error || 'Errore durante la generazione della risposta') + details);
        }
        
        const response = generationData.response;
        console.log('✅ Risposta generata con successo');
        
        // Aggiungi messaggio assistente
        addMessage('assistant', response, relevantChunks);
        
        // Aggiorna cronologia per multi-turn
        chatHistory.push({
            role: 'user',
            text: query
        });
        chatHistory.push({
            role: 'model',
            text: response
        });
        
        // Mantieni solo le ultime 10 interazioni (20 messaggi)
        if (chatHistory.length > 20) {
            chatHistory = chatHistory.slice(-20);
        }
        
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
                        ${uniqueSources.map(src => `<li>${escapeHtml(src)}</li>`).join('')}
                    </ul>
                    <small>${sources.length} frammenti utilizzati</small>
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
        const container = document.getElementById('messages-container');
        container.innerHTML = `
            <div class="welcome-message">
                <div class="welcome-icon">🤖</div>
                <h2>Benvenuto nel Chatbot RAG!</h2>
                <p>Sono qui per aiutarti a trovare informazioni nei tuoi documenti.</p>
                <p class="welcome-hint">Fai una domanda per iniziare...</p>
            </div>
        `;
        chatHistory = [];
        showToast('Conversazione cancellata', 'success');
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
