# Google File Search - Guida Docker

Questa guida fornisce le istruzioni per eseguire il progetto Google File Search con Docker Desktop.

## Prerequisiti

1. **Docker Desktop** installato e in esecuzione
   - Windows: [Scarica Docker Desktop per Windows](https://www.docker.com/products/docker-desktop)
   - Mac: [Scarica Docker Desktop per Mac](https://www.docker.com/products/docker-desktop)
   - Linux: [Installa Docker Engine](https://docs.docker.com/engine/install/)

2. **File .env configurato**
   - Copia `.env.example` in `.env`
   - Configura le seguenti variabili obbligatorie:
     ```bash
     GEMINI_API_KEY=your_api_key_here
     FILE_SEARCH_STORE_NAME=fileSearchStores/your-store-name
     ```

## Architettura Docker

Il progetto utilizza Docker Compose con due servizi principali:

```
┌─────────────────────────────────────────────┐
│           Docker Desktop                    │
│                                             │
│  ┌─────────────┐         ┌──────────────┐  │
│  │  Frontend   │         │   Backend    │  │
│  │  (Nginx)    │────────▶│   (Flask)    │  │
│  │  Port: 80   │  Proxy  │  Port: 5000  │  │
│  └─────────────┘         └──────────────┘  │
│                                             │
│  Network: app-network                       │
│  Volume: uploads_data                       │
└─────────────────────────────────────────────┘
```

### Servizi

1. **Backend** (`googlefilesearch-backend`)
   - Immagine: Python 3.11 slim
   - Flask + Gunicorn (4 workers)
   - Porta: 5000
   - Volume: `/app/uploads` (per file temporanei)

2. **Frontend** (`googlefilesearch-frontend`)
   - Immagine: Node 20 (build) + Nginx Alpine (serve)
   - React SPA con routing
   - Porta: 80
   - Proxy API verso backend

## Comandi Quick Start

### 1. Prima Esecuzione

```bash
# 1. Configura il file .env
cp .env.example .env
# Modifica .env con i tuoi valori

# 2. Build e avvio dei container
docker-compose up -d --build

# 3. Verifica lo stato dei container
docker-compose ps

# 4. Visualizza i logs
docker-compose logs -f
```

L'applicazione sarà disponibile su:
- **Frontend**: http://localhost
- **Backend API**: http://localhost:5000

### 2. Comandi di Base

```bash
# Avvio dei container (senza rebuild)
docker-compose up -d

# Stop dei container
docker-compose stop

# Stop e rimozione dei container
docker-compose down

# Stop, rimozione e pulizia volumi
docker-compose down -v

# Rebuild dei container
docker-compose build

# Rebuild senza cache
docker-compose build --no-cache

# Restart di un singolo servizio
docker-compose restart backend
docker-compose restart frontend
```

### 3. Visualizzare i Logs

```bash
# Logs di tutti i servizi
docker-compose logs -f

# Logs solo del backend
docker-compose logs -f backend

# Logs solo del frontend
docker-compose logs -f frontend

# Ultimi 100 log
docker-compose logs --tail=100
```

### 4. Accesso ai Container

```bash
# Shell nel container backend
docker-compose exec backend /bin/bash

# Shell nel container frontend
docker-compose exec frontend /bin/sh

# Esegui comando nel backend
docker-compose exec backend python test_api.py
```

### 5. Health Check

```bash
# Verifica lo stato di salute
docker-compose ps

# Test manuale endpoint backend
curl http://localhost:5000/api/config

# Test manuale frontend
curl http://localhost
```

## Configurazione Avanzata

### Variabili d'Ambiente

Modifica il file `.env` per configurare il comportamento dell'applicazione:

```bash
# API Configuration
GEMINI_API_KEY=your_api_key_here
FILE_SEARCH_STORE_NAME=fileSearchStores/your-store-name
DEFAULT_MODEL=gemini-2.5-pro

# Chunking Configuration
CHUNK_SIZE=800
CHUNK_OVERLAP_PERCENT=10

# RAG Configuration
RESULTS_COUNT=25
MIN_RELEVANCE_SCORE=0.3
MAX_CHUNKS_FOR_GENERATION=15
```

### Personalizzare le Porte

Per modificare le porte esposte, edita `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "8080:5000"  # Cambia 8080 con la porta desiderata
  frontend:
    ports:
      - "8000:80"    # Cambia 8000 con la porta desiderata
```

### Aumentare i Worker Gunicorn

Edita `backend/Dockerfile`:

```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "8", ...]
```

### Configurare Nginx

Modifica `frontend-react/nginx.conf` per:
- Timeout delle richieste API
- Configurazione cache
- Headers personalizzati

## Sviluppo con Docker

### Hot Reload (Development Mode)

Per sviluppare con hot reload, usa un docker-compose override:

```bash
# Crea docker-compose.override.yml
cat > docker-compose.override.yml << EOF
version: '3.8'
services:
  backend:
    command: flask run --host=0.0.0.0 --port=5000 --reload
    environment:
      - FLASK_ENV=development
    volumes:
      - ./backend:/app
  frontend:
    command: npm run dev
    ports:
      - "5173:5173"
    volumes:
      - ./frontend-react:/app
      - /app/node_modules
EOF

# Avvia in modalità development
docker-compose up
```

### Debug

```bash
# Logs in tempo reale con timestamp
docker-compose logs -f --timestamps

# Inspect di un container
docker inspect googlefilesearch-backend

# Statistiche di utilizzo risorse
docker stats

# Verifica network
docker network inspect googlefilesearch_app-network
```

## Troubleshooting

### Problema: Container backend non si avvia

**Sintomo**: `docker-compose ps` mostra backend come `Exit 1`

**Soluzione**:
```bash
# Verifica i logs
docker-compose logs backend

# Verifica il file .env
cat .env

# Rebuild del container
docker-compose build --no-cache backend
docker-compose up -d backend
```

### Problema: Errore "Permission denied" sui volumi

**Sintomo**: Errore di scrittura in `/app/uploads`

**Soluzione**:
```bash
# Linux: assicurati che i permessi siano corretti
docker-compose exec backend chmod 777 /app/uploads

# Oppure rimuovi e ricrea il volume
docker-compose down -v
docker-compose up -d
```

### Problema: Porta già in uso

**Sintomo**: `Error: bind: address already in use`

**Soluzione**:
```bash
# Windows: trova il processo che usa la porta
netstat -ano | findstr :80
netstat -ano | findstr :5000

# Linux/Mac: trova il processo
lsof -i :80
lsof -i :5000

# Termina il processo o cambia porta in docker-compose.yml
```

### Problema: Frontend non comunica con backend

**Sintomo**: Errori 502 Bad Gateway o timeout API

**Soluzione**:
```bash
# Verifica che backend sia healthy
docker-compose ps

# Testa connessione diretta al backend
curl http://localhost:5000/api/config

# Verifica network
docker network inspect googlefilesearch_app-network

# Restart dei servizi
docker-compose restart
```

### Problema: Build frontend fallisce

**Sintomo**: `npm run build` fallisce durante docker build

**Soluzione**:
```bash
# Pulisci cache Docker
docker system prune -a --volumes

# Build con output verbose
docker-compose build --no-cache --progress=plain frontend

# Verifica package.json
docker-compose run --rm frontend npm install
```

### Problema: Upload di file grandi fallisce

**Sintomo**: Timeout su upload > 10MB

**Soluzione**:
Edita `frontend-react/nginx.conf`:
```nginx
location /api/ {
    ...
    client_max_body_size 100M;  # Aumenta limite upload
    proxy_request_buffering off;
    ...
}
```

Rebuild frontend:
```bash
docker-compose build frontend
docker-compose up -d frontend
```

## Manutenzione

### Backup dei Dati

```bash
# Backup volume uploads
docker run --rm -v googlefilesearch_uploads_data:/data \
  -v $(pwd):/backup alpine tar czf /backup/uploads-backup.tar.gz /data

# Restore volume uploads
docker run --rm -v googlefilesearch_uploads_data:/data \
  -v $(pwd):/backup alpine tar xzf /backup/uploads-backup.tar.gz -C /
```

### Pulizia Docker

```bash
# Rimuovi container stopped
docker container prune

# Rimuovi immagini unused
docker image prune -a

# Rimuovi volumi unused
docker volume prune

# Pulizia completa sistema
docker system prune -a --volumes
```

### Aggiornamento delle Immagini

```bash
# Pull delle ultime immagini base
docker-compose pull

# Rebuild con ultime immagini
docker-compose build --pull --no-cache

# Restart con nuove immagini
docker-compose up -d
```

## Deployment in Produzione

### Best Practices

1. **Usa variabili d'ambiente sicure**
   ```bash
   # Non committare .env in git
   echo ".env" >> .gitignore

   # Usa secrets management (Docker Swarm, Kubernetes, etc.)
   ```

2. **Abilita HTTPS con reverse proxy**
   ```bash
   # Usa Traefik o Nginx come reverse proxy
   # Configura Let's Encrypt per certificati SSL
   ```

3. **Limita risorse container**
   ```yaml
   services:
     backend:
       deploy:
         resources:
           limits:
             cpus: '2'
             memory: 2G
   ```

4. **Monitoring e logging**
   ```bash
   # Usa strumenti come Prometheus, Grafana, ELK stack
   # Configura log aggregation
   ```

5. **Backup automatici**
   ```bash
   # Configura cronjob per backup periodici
   # Usa storage cloud (S3, Google Cloud Storage)
   ```

## Risorse Aggiuntive

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Best Practices Dockerfile](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [README.md principale](README.md) - Documentazione applicazione
- [CLAUDE.md](CLAUDE.md) - Documentazione sviluppo

## Supporto

Per problemi o domande:
1. Controlla la sezione Troubleshooting sopra
2. Verifica i logs: `docker-compose logs -f`
3. Consulta la documentazione Docker Desktop
4. Apri una issue su GitHub (se applicabile)

---

**Nota**: Questa guida assume l'uso di Docker Compose V2 (integrato in Docker Desktop). Se usi Docker Compose V1, sostituisci `docker-compose` con `docker compose` (senza trattino).
