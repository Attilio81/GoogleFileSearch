# PROGETTO: Migrazione Frontend a React 19 PWA

Devi creare una Progressive Web App (PWA) con React 19, Vite, e Material UI (Google Material Design 3) per sostituire il frontend vanilla JavaScript di un sistema RAG (Retrieval Augmented Generation) basato su Google Gemini File Search API.

## REQUISITI TECNICI

### Stack Obbligatorio:
- **React 19** (ultima versione con nuove features)
- **Vite 5+** (build tool e dev server)
- **Material UI v6** (MUI - Google Material Design 3)
- **PWA** con Workbox (installabile, offline-first)
- **React Router v6** (SPA routing)
- **TanStack Query v5** (React Query - gestione stato server)
- **Axios** (HTTP client)

### Configurazione Iniziale:

1. Crea nuovo progetto nella cartella `frontend-react/`:
```bash
npm create vite@latest frontend-react -- --template react
cd frontend-react
npm install
```

2. Installa dipendenze:
```bash
npm install @mui/material @emotion/react @emotion/styled @mui/icons-material
npm install react-router-dom @tanstack/react-query axios
npm install -D @vite-pwa/vite-plugin workbox-window
npm install react-markdown react-hook-form @hookform/resolvers zod
```

3. Configurazione Vite (`vite.config.js`):
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.svg', 'robots.txt', 'apple-touch-icon.png'],
      manifest: {
        name: 'Google RAG File Search',
        short_name: 'RAG Search',
        description: 'Sistema di gestione documenti con AI RAG',
        theme_color: '#1976d2',
        background_color: '#ffffff',
        display: 'standalone',
        icons: [
          {
            src: 'pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png'
          }
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg}'],
        runtimeCaching: [
          {
            urlPattern: /^http:\/\/localhost:5000\/api\/.*/i,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              expiration: {
                maxEntries: 50,
                maxAgeSeconds: 60 * 5 // 5 minuti
              }
            }
          }
        ]
      }
    })
  ],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: '../backend/static/dist',
    emptyOutDir: true
  }
})
```

## BACKEND API ENDPOINTS

Il backend Flask espone questi endpoint REST:

### Configurazione
- `GET /api/config` → Ritorna configurazione RAG (chunk_size, model, etc.)

### Documenti
- `GET /api/documents?pageSize=20&pageToken=xxx` → Lista documenti (paginata)
  Response: `{success: bool, documents: [...], nextPageToken: string}`
  
- `POST /api/documents/upload` → Upload documento (multipart/form-data)
  FormData: {file, displayName, mimeType, chunkSize, documentLocation, metadataKeys[], metadataValues[]}
  Response: `{success: bool, operation_name: string, document_name: string}`

- `GET /api/operations/{operation_name}` → Stato operazione upload
  Response: `{success: bool, done: bool, state: string, error?: object}`

- `DELETE /api/documents/{document_name}?force=true` → Elimina documento

- `POST /api/documents/{document_name}/chunks` → Query chunks in documento
  Body: `{query: string, results_count: number}`
  Response: `{success: bool, chunks: [{chunk: object, chunkRelevanceScore: number, source_document: string}]}`

### Chat RAG
- `POST /api/chat/query` → Fase 1: Retrieval chunks rilevanti
  Body: `{query: string, document_name?: string, results_count?: number}`
  Response: `{success: bool, relevant_chunks: [...], query: string}`

- `POST /api/chat/generate` → Fase 2: Generazione risposta AI
  Body: `{query: string, relevant_chunks: [...], model?: string}`
  Response: `{success: bool, response: string, chunks_used: number, chunks_filtered: [...]}`

- `POST /api/chat/generate-stream` → Streaming SSE risposta AI
  Body: identico a /generate
  Response: Server-Sent Events con `data: {text: string}` e `data: {done: true}`

## STRUTTURA COMPONENTI RICHIESTA

### Layout e Routing
```
App.jsx
├── ThemeProvider (MUI dark/light mode)
├── Router
    ├── Layout (AppBar + Drawer + Footer)
    │   ├── /documents → DocumentsPage
    │   ├── /chat → ChatPage
    │   └── /chunks → ChunksPage
    └── NotFound
```

### 1. DocumentsPage (pagina principale)

**Componenti:**
- `DocumentsPage.jsx` - Container principale
- `DocumentList.jsx` - Tabella/Grid documenti con MUI DataGrid o Table
- `DocumentUploadDialog.jsx` - Dialog upload con stepper
- `DocumentCard.jsx` - Card singolo documento (mobile)
- `OperationProgress.jsx` - Progress indicator per upload
- `DeleteConfirmDialog.jsx` - Dialog conferma eliminazione

**Features:**
- Lista documenti con paginazione (nextPageToken)
- Upload con drag&drop (MUI Dropzone style)
- Form metadati dinamici (add/remove con IconButton)
- Polling automatico operazioni con React Query
- Filtri e ricerca locale
- Responsive: Table desktop, Cards mobile
- Skeleton loaders durante fetch
- Snackbar notifiche successo/errore

### 2. ChatPage (chatbot RAG)

**Componenti:**
- `ChatPage.jsx` - Container con layout chat
- `MessageList.jsx` - Lista messaggi scrollabile
- `MessageBubble.jsx` - Singolo messaggio (user/assistant)
- `SourcesAccordion.jsx` - Accordion MUI per fonti
- `ChatInput.jsx` - TextField + IconButton send
- `ChatSettingsDrawer.jsx` - Drawer impostazioni (model, results_count)
- `StreamingIndicator.jsx` - Animazione "typing..."

**Features:**
- Chat history persistente (localStorage)
- Streaming SSE con effect typing
- Render markdown nelle risposte (react-markdown)
- Sources expandable con relevance score
- Settings: model selector, results count slider
- Auto-scroll su nuovo messaggio
- Copy message button
- Clear history con conferma
- Session ID univoco

### 3. ChunksPage (visualizzatore chunks)

**Componenti:**
- `ChunksPage.jsx` - Container
- `DocumentSelector.jsx` - Autocomplete MUI documenti
- `ChunkList.jsx` - Grid chunks con infinite scroll
- `ChunkCard.jsx` - Card chunk con score badge
- `SearchBar.jsx` - TextField debounced

**Features:**
- Select documento da lista
- Search bar con debounce (500ms)
- Grid chunks responsive
- Score badge colorato (green >0.7, yellow >0.4, red <0.4)
- Infinite scroll o pagination
- Copy chunk text
- Filter per min score

### 4. Layout Components

**AppBarCustom.jsx:**
- MUI AppBar con logo, titolo, navigation tabs
- IconButton menu mobile (hamburger)
- Theme toggle button (dark/light)
- Install PWA button (quando disponibile)

**DrawerNavigation.jsx:**
- MUI Drawer responsive
- Navigation items con icons:
  - 📄 Documents
  - 💬 Chat
  - 📦 Chunks
- Active route highlighting

**Footer.jsx:**
- Info progetto
- Link GitHub
- Versione app

## CUSTOM HOOKS RICHIESTI

### `hooks/useDocuments.js`
```javascript
// React Query hooks per:
// - useDocuments(pageToken) → fetch lista
// - useUploadDocument() → mutation upload
// - useDeleteDocument() → mutation delete
// - useOperationStatus(operationName) → polling ogni 3s
```

### `hooks/useChat.js`
```javascript
// React Query hooks per:
// - useQueryChunks(query) → fase retrieval
// - useGenerateResponse(query, chunks, streaming) → fase generation
// - useChatHistory() → localStorage sync
```

### `hooks/useChunks.js`
```javascript
// - useDocumentChunks(documentName, query)
```

### `hooks/usePWA.js`
```javascript
// - Rileva se PWA installabile
// - Mostra prompt installazione
// - Gestisce beforeinstallprompt event
```

### `hooks/useDebounce.js`
```javascript
// Debounce generico per search inputs
```

## SERVIZI

### `services/api.js`
```javascript
// Axios instance configurato:
// - baseURL: '/api' (proxy Vite)
// - interceptors per errors
// - helper functions per ogni endpoint
```

### `services/pwa.js`
```javascript
// Workbox service worker registration
// Update notifications
```

## TEMA MUI

### `theme/theme.js`
```javascript
// Material Design 3 theme:
// - Primary: #1976d2 (Google Blue)
// - Secondary: #dc004e
// - Dark mode support
// - Typography custom (Roboto)
// - Component overrides per consistency
```

## FORM VALIDATION

Usa **react-hook-form** + **zod** per validazione:

Schema validazione upload:
- File: required, max 100MB
- displayName: max 512 chars
- mimeType: optional, pattern regex
- metadataKeys: unique, max 50 items

## PWA FEATURES OBBLIGATORIE

1. **Installable:** Manifest + service worker
2. **Offline-first:** Cache API responses (NetworkFirst strategy)
3. **Update notification:** Snackbar "Nuova versione disponibile - Aggiorna"
4. **Add to Home Screen button:** Visible quando PWA installabile
5. **Splash screen:** Configurato in manifest
6. **Icons:** 192x192 e 512x512 PNG

## RESPONSIVE DESIGN

- **Desktop (>1280px):** Drawer permanente, Table view
- **Tablet (768-1279px):** Drawer collapsible, Grid view
- **Mobile (<768px):** Bottom navigation, Card view, dialog full-screen

## PERFORMANCE REQUIREMENTS

- **Code splitting:** React.lazy() per routes
- **Memoization:** React.memo, useMemo, useCallback dove appropriato
- **Virtualization:** react-window per liste lunghe (se >100 items)
- **Image optimization:** Lazy loading immagini
- **Bundle size target:** <500KB gzipped

## ACCESSIBILITY (A11Y)

- Tutti i button con aria-label
- Form fields con proper labels
- Keyboard navigation support
- Focus management nei dialog
- Color contrast WCAG AA compliant

## ERROR HANDLING

- Error boundaries per ogni route
- Toast notifications (MUI Snackbar)
- Fallback UI per errori API
- Retry button su errori network
- Validation errors inline nei form

## TESTING (opzionale ma consigliato)

```bash
npm install -D vitest @testing-library/react @testing-library/user-event
```

Test critici:
- Upload flow completo
- Chat query + streaming
- Pagination documenti

## BUILD E DEPLOY

1. Build production:
```bash
npm run build
# Output in: ../backend/static/dist/
```

2. Flask serve React:
Aggiungi in `backend/app.py`:
```python
# Fallback route per SPA
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path and os.path.exists(os.path.join(app.static_folder, 'dist', path)):
        return send_from_directory(os.path.join(app.static_folder, 'dist'), path)
    return send_from_directory(os.path.join(app.static_folder, 'dist'), 'index.html')
```

## STATO INIZIALE

Fornisco le info sul backend esistente:
- API già REST-ful e ben documentate
- CORS già configurato
- Streaming SSE già implementato
- Rate limiting e cache già attivi
- Validazione input già presente

## OUTPUT RICHIESTO

Genera il codice completo per:

**FASE 1 - Setup (inizia da qui):**
1. `package.json` completo
2. `vite.config.js` con PWA
3. `src/main.jsx` entry point
4. `src/App.jsx` con routing
5. `src/theme/theme.js` Material UI theme
6. `src/services/api.js` axios setup

**FASE 2 - Documents (dopo conferma Fase 1):**
7. `DocumentsPage.jsx` + tutti i sub-components
8. `hooks/useDocuments.js`
9. Form upload completo con validazione

**FASE 3 - Chat (dopo conferma Fase 2):**
10. `ChatPage.jsx` + components
11. `hooks/useChat.js`
12. Streaming SSE implementation

**FASE 4 - Chunks + Polish (dopo conferma Fase 3):**
13. `ChunksPage.jsx`
14. Layout components (AppBar, Drawer, Footer)
15. PWA setup finale + icons

## NOTE IMPORTANTI

- **Usa TypeScript se possibile** (altrimenti JavaScript moderno)
- **Commenta codice complesso** (es: polling logic, streaming)
- **Gestisci edge cases** (no documents, no chunks, API down)
- **Mobile-first approach** per CSS/layout
- **Dark mode di default** (salvato in localStorage)

## DOMANDE PRIMA DI INIZIARE

1. Preferisci TypeScript o JavaScript?
2. Vuoi test automatici (Vitest)?
3. Serve i18n (internazionalizzazione)?
4. Limiti specifici di compatibilità browser?

Procedi con FASE 1 quando sei pronto!

---

## 📦 Quick Start Commands

```bash
# 1. Crea progetto
cd "c:\Progetti Pilota\Gestione Documenti GoogleSearch"
npm create vite@latest frontend-react -- --template react

# 2. Installa tutto
cd frontend-react
npm install @mui/material @emotion/react @emotion/styled @mui/icons-material
npm install react-router-dom @tanstack/react-query axios
npm install -D @vite-pwa/vite-plugin workbox-window
npm install react-markdown react-hook-form @hookform/resolvers zod

# 3. Avvia dev server
npm run dev

# 4. (in parallelo) Avvia backend Flask
cd ../backend
python app.py
```

## 🎯 Workflow Consigliato

1. **Fase 1 (30 min):** Setup + configurazione base
2. **Fase 2 (1h):** Pagina documenti completa
3. **Fase 3 (1.5h):** Chat interface con streaming
4. **Fase 4 (1h):** Chunks viewer + polish finale

**Totale stimato:** 4-6 ore con AI coding assistant

## 🎨 Material UI Resources

- **MUI Docs:** https://mui.com/material-ui/
- **Color Tool:** https://m2.material.io/design/color/
- **Icons:** https://mui.com/material-ui/material-icons/
- **Templates:** https://mui.com/material-ui/getting-started/templates/

## ✅ Checklist Finale

Prima del deploy, verifica:
- [ ] PWA installabile (manifest + SW)
- [ ] Funziona offline (cache API)
- [ ] Responsive su mobile/tablet/desktop
- [ ] Dark mode funzionante
- [ ] Streaming chat funziona
- [ ] Upload con progress bar
- [ ] Polling operations attivo
- [ ] Error handling robusto
- [ ] Bundle < 500KB gzipped
- [ ] Lighthouse score > 90
