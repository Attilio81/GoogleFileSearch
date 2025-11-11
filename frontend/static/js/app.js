// Configurazione
const API_BASE = 'http://localhost:5000/api';
let activeOperations = new Map();
let documentToDelete = null;

// Inizializzazione
document.addEventListener('DOMContentLoaded', () => {
    loadConfig();
    loadDocuments();
    setupUploadForm();
    startOperationsPolling();
});

// Carica configurazione
async function loadConfig() {
    try {
        const response = await fetch(`${API_BASE}/config`);
        const data = await response.json();
        
        if (data.success) {
            const configInfo = document.getElementById('config-info');
            configInfo.innerHTML = `
                <strong>Store:</strong> ${data.store_name} | 
                <strong>API:</strong> ${data.api_configured ? '✅ Configurata' : '❌ Non configurata'}
            `;
        }
    } catch (error) {
        console.error('Errore caricamento configurazione:', error);
    }
}

// Setup form upload
function setupUploadForm() {
    const form = document.getElementById('upload-form');
    form.addEventListener('submit', handleUpload);
}

// Gestione upload
async function handleUpload(e) {
    e.preventDefault();
    
    const form = e.target;
    const uploadBtn = document.getElementById('upload-btn');
    const statusDiv = document.getElementById('upload-status');
    
    // Crea FormData manuale filtrando metadati vuoti
    const formData = new FormData();
    
    // Aggiungi file e displayName
    const fileInput = form.querySelector('input[type="file"]');
    const displayNameInput = form.querySelector('input[name="displayName"]');
    const chunkSizeSelect = form.querySelector('select[name="chunkSize"]');
    
    formData.append('file', fileInput.files[0]);
    if (displayNameInput.value) {
        formData.append('displayName', displayNameInput.value);
    }
    
    // Aggiungi configurazione chunking
    if (chunkSizeSelect && chunkSizeSelect.value) {
        formData.append('chunkSize', chunkSizeSelect.value);
    }
    
    // Aggiungi posizione documento come metadata speciale (se presente)
    const documentLocationInput = form.querySelector('input[name="documentLocation"]');
    if (documentLocationInput && documentLocationInput.value.trim()) {
        formData.append('metadataKeys[]', 'document_location');
        formData.append('metadataValues[]', documentLocationInput.value.trim());
    }
    
    // Filtra e aggiungi solo metadati non vuoti
    const metadataKeys = form.querySelectorAll('input[name="metadataKeys[]"]');
    const metadataValues = form.querySelectorAll('input[name="metadataValues[]"]');
    
    metadataKeys.forEach((keyInput, index) => {
        const key = keyInput.value.trim();
        const value = metadataValues[index].value.trim();
        
        // Aggiungi solo se entrambi sono non vuoti
        if (key && value) {
            formData.append('metadataKeys[]', key);
            formData.append('metadataValues[]', value);
        }
    });
    
    // Disabilita pulsante e mostra loader
    uploadBtn.disabled = true;
    uploadBtn.querySelector('.btn-text').textContent = 'Caricamento...';
    uploadBtn.querySelector('.loader').style.display = 'inline-block';
    statusDiv.style.display = 'none';
    
    try {
        const response = await fetch(`${API_BASE}/documents/upload`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            showStatus('success', data.message);
            
            // Aggiungi operazione al tracking
            if (data.operationName) {
                trackOperation(data.operationName, formData.get('displayName') || formData.get('file').name);
            }
            
            // Reset form
            form.reset();
            
            // Non è necessario aggiornare la lista qui, ci pensa il poller
            // setTimeout(() => loadDocuments(), 2000);
        } else {
            showStatus('error', `Errore: ${data.error}`);
            if (data.details) {
                console.error('Dettagli errore:', data.details);
            }
        }
    } catch (error) {
        showStatus('error', `Errore di rete: ${error.message}`);
        console.error('Errore upload:', error);
    } finally {
        uploadBtn.disabled = false;
        uploadBtn.querySelector('.btn-text').textContent = 'Carica Documento';
        uploadBtn.querySelector('.loader').style.display = 'none';
    }
}

// Mostra messaggio di stato
function showStatus(type, message) {
    const statusDiv = document.getElementById('upload-status');
    statusDiv.className = `status-message ${type}`;
    statusDiv.textContent = message;
    statusDiv.style.display = 'block';
    
    // Nascondi dopo 5 secondi per i messaggi di successo
    if (type === 'success') {
        setTimeout(() => {
            statusDiv.style.display = 'none';
        }, 5000);
    }
}

// Tracking operazioni
function trackOperation(operationName, displayName) {
    activeOperations.set(operationName, {
        name: operationName,
        displayName: displayName,
        startTime: new Date()
    });
    
    updateOperationsDisplay();
}

// Aggiorna visualizzazione operazioni
function updateOperationsDisplay() {
    const section = document.getElementById('operations-section');
    const list = document.getElementById('operations-list');
    
    if (activeOperations.size === 0) {
        section.style.display = 'none';
        return;
    }
    
    section.style.display = 'block';
    list.innerHTML = '';
    
    activeOperations.forEach((op, name) => {
        const card = document.createElement('div');
        card.className = 'operation-card';
        card.id = `op-${name.replace(/\//g, '-')}`;
        
        const elapsed = Math.floor((new Date() - op.startTime) / 1000);
        
        card.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>${op.displayName}</strong>
                    <div style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 5px;">
                        ⏱️ Elaborazione in corso... (${elapsed}s)
                    </div>
                </div>
                <div class="loader"></div>
            </div>
        `;
        
        list.appendChild(card);
    });
}

// Polling operazioni
async function startOperationsPolling() {
    setInterval(async () => {
        if (activeOperations.size === 0) return;
        
        const operations = Array.from(activeOperations.keys());
        
        for (const opName of operations) {
            await checkOperationStatus(opName);
        }
        
        updateOperationsDisplay();
    }, 3000); // Controlla ogni 3 secondi
}

// Controlla stato operazione
async function checkOperationStatus(operationName) {
    try {
        const response = await fetch(`${API_BASE}/operations/${operationName}`);
        const data = await response.json();
        
        if (data.success && data.done) {
            const op = activeOperations.get(operationName);
            const card = document.getElementById(`op-${operationName.replace(/\//g, '-')}`);
            
            if (data.error) {
                // Operazione fallita
                if (card) {
                    card.className = 'operation-card error';
                    card.innerHTML = `
                        <div>
                            <strong>${op.displayName}</strong>
                            <div style="font-size: 0.85rem; color: var(--danger-color); margin-top: 5px;">
                                ❌ Errore: ${data.error.message || 'Operazione fallita'}
                            </div>
                        </div>
                    `;
                }
                
                // Rimuovi dopo 10 secondi
                setTimeout(() => {
                    activeOperations.delete(operationName);
                    updateOperationsDisplay();
                }, 10000);
            } else {
                // Operazione completata con successo
                if (card) {
                    card.className = 'operation-card done';
                    card.innerHTML = `
                        <div>
                            <strong>${op.displayName}</strong>
                            <div style="font-size: 0.85rem; color: var(--success-color); margin-top: 5px;">
                                ✅ Documento pronto per la ricerca
                            </div>
                        </div>
                    `;
                }
                
                activeOperations.delete(operationName);
                
                // Aggiorna lista documenti
                setTimeout(() => {
                    loadDocuments();
                    updateOperationsDisplay();
                }, 2000);
            }
        }
    } catch (error) {
        console.error('Errore controllo operazione:', error);
    }
}

// Carica lista documenti
// Variabili per la paginazione
let currentPageToken = '';
let currentPageSize = 20;

async function loadDocuments(pageToken = '', pageSize = currentPageSize) {
    const statusDiv = document.getElementById('documents-status');
    const table = document.getElementById('documents-table');
    const tbody = document.getElementById('documents-tbody');
    
    statusDiv.textContent = 'Caricamento documenti in corso...';
    statusDiv.style.display = 'block';
    table.style.display = 'none';
    
    try {
        let url = `${API_BASE}/documents?pageSize=${pageSize}`;
        if (pageToken) {
            url += `&pageToken=${encodeURIComponent(pageToken)}`;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.success) {
            if (data.documents && data.documents.length > 0) {
                tbody.innerHTML = '';
                
                data.documents.forEach(doc => {
                    const row = createDocumentRow(doc);
                    tbody.appendChild(row);
                });
                
                // Aggiorna token di paginazione
                currentPageToken = data.nextPageToken || '';
                currentPageSize = pageSize;
                
                // Mostra/nascondi controlli paginazione
                updatePaginationControls();
                
                statusDiv.style.display = 'none';
                table.style.display = 'table';
            } else {
                statusDiv.textContent = 'Nessun documento trovato. Carica il primo documento!';
                table.style.display = 'none';
            }
        } else {
            statusDiv.className = 'status-message error';
            statusDiv.textContent = `Errore: ${data.error}`;
        }
    } catch (error) {
        statusDiv.className = 'status-message error';
        statusDiv.textContent = `Errore di rete: ${error.message}`;
        console.error('Errore caricamento documenti:', error);
    }
}

function updatePaginationControls() {
    const paginationDiv = document.getElementById('pagination-controls');
    const nextBtn = document.getElementById('next-page-btn');
    
    if (currentPageToken) {
        paginationDiv.style.display = 'block';
        nextBtn.style.display = 'inline-block';
    } else {
        paginationDiv.style.display = 'none';
        nextBtn.style.display = 'none';
    }
}

function loadNextPage() {
    if (currentPageToken) {
        loadDocuments(currentPageToken, currentPageSize);
    }
}

// Crea riga tabella documento
function createDocumentRow(doc) {
    const row = document.createElement('tr');
    
    // Estrai ID documento
    const docId = doc.name.split('/').pop();
    
    // Formatta dimensione
    const sizeKB = (doc.sizeBytes / 1024).toFixed(2);
    const sizeMB = (doc.sizeBytes / (1024 * 1024)).toFixed(2);
    const sizeDisplay = doc.sizeBytes > 1024 * 1024 ? `${sizeMB} MB` : `${sizeKB} KB`;
    
    // Formatta data
    const date = new Date(doc.createTime);
    const dateDisplay = date.toLocaleString('it-IT');
    
    // Stato
    const stateClass = doc.state === 'STATE_ACTIVE' ? 'state-active' : 
                       doc.state === 'STATE_PENDING' ? 'state-pending' : 'state-failed';
    const stateText = doc.state === 'STATE_ACTIVE' ? '✅ Attivo' : 
                      doc.state === 'STATE_PENDING' ? '⏳ In elaborazione' : '❌ Fallito';
    
    // Escape HTML per sicurezza
    const displayNameEscaped = (doc.displayName || 'N/A').replace(/'/g, '&#39;').replace(/"/g, '&quot;');
    const displayNameForTitle = doc.displayName || 'N/A';
    
    row.innerHTML = `
        <td><span class="text-truncate" title="${docId}">${docId}</span></td>
        <td><strong title="${displayNameForTitle}">${displayNameEscaped}</strong></td>
        <td style="white-space: nowrap;">${sizeDisplay}</td>
        <td style="white-space: nowrap;"><span class="state-badge ${stateClass}">${stateText}</span></td>
        <td style="white-space: nowrap;">${dateDisplay}</td>
        <td style="white-space: nowrap;">
            <button class="btn btn-danger btn-small" onclick="openDeleteModal('${doc.name.replace(/'/g, "\\'")}', '${displayNameEscaped}')">
                🗑️ Elimina
            </button>
        </td>
    `;
    
    return row;
}

// Refresh documenti
async function refreshDocuments() {
    const icon = document.getElementById('refresh-icon');
    icon.classList.add('animate-spin');
    
    await loadDocuments();
    
    setTimeout(() => {
        icon.classList.remove('animate-spin');
    }, 1000);
}

// Modal eliminazione
function openDeleteModal(docName, displayName) {
    documentToDelete = docName;
    document.getElementById('delete-doc-name').textContent = displayName;
    document.getElementById('delete-modal').style.display = 'flex';
}

function closeDeleteModal() {
    documentToDelete = null;
    document.getElementById('delete-modal').style.display = 'none';
}

// Conferma eliminazione
async function confirmDelete() {
    if (!documentToDelete) return;
    
    const modal = document.getElementById('delete-modal');
    
    try {
        const response = await fetch(`${API_BASE}/documents/${documentToDelete}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            closeDeleteModal();
            showStatus('success', 'Documento eliminato con successo');
            loadDocuments();
        } else {
            alert(`Errore durante l'eliminazione: ${data.error}`);
        }
    } catch (error) {
        alert(`Errore di rete: ${error.message}`);
        console.error('Errore eliminazione:', error);
    }
}

// Gestione metadati custom
function addMetadataRow() {
    const container = document.getElementById('metadata-container');
    const newRow = document.createElement('div');
    newRow.className = 'metadata-row';
    newRow.innerHTML = `
        <input type="text" name="metadataKeys[]" placeholder="Chiave" class="metadata-key">
        <input type="text" name="metadataValues[]" placeholder="Valore" class="metadata-value">
        <button type="button" class="btn-small btn-remove" onclick="removeMetadataRow(this)">-</button>
    `;
    container.appendChild(newRow);
}

function removeMetadataRow(button) {
    button.parentElement.remove();
}

// Gestione eventi globali
window.addEventListener('error', (event) => {
    console.error('Errore globale:', event.error);
});

// Chiudi modal con ESC
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeDeleteModal();
    }
});
