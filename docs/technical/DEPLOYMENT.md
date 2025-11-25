# 🚀 Guida al Deployment in Produzione

Guida completa per il rilascio e l'installazione di Google File Search RAG su server Windows e Linux.

---

## 📋 Indice

- [Windows Server](#windows-server)
  - [Setup Base](#1-setup-base)
  - [Servizio Windows con NSSM](#2-installazione-come-servizio-windows)
  - [Waitress WSGI Server](#3-produzione-con-waitress)
  - [Firewall e Sicurezza](#4-configurazione-firewall)
  - [Reverse Proxy IIS](#5-reverse-proxy-con-iis-opzionale)
- [Linux Server](#linux-server)
  - [Setup Base](#1-setup-base-1)
  - [Servizio Systemd](#2-installazione-come-servizio-systemd)
  - [Gunicorn WSGI Server](#3-produzione-con-gunicorn)
  - [Nginx Reverse Proxy](#4-reverse-proxy-con-nginx)
  - [SSL/HTTPS](#5-sslhttps-con-certbot)
- [Monitoraggio e Manutenzione](#monitoraggio-e-manutenzione)
- [Backup e Disaster Recovery](#backup-e-disaster-recovery)
- [Sicurezza Best Practices](#sicurezza-best-practices)

---

## 🪟 Windows Server

### 1. Setup Base

#### Requisiti
- Windows Server 2016+ o Windows 10/11
- Python 3.8+
- 1GB RAM minimo (2GB consigliato)
- 1GB spazio disco

#### Installazione

```powershell
# 1. Scarica il progetto
git clone https://github.com/Attilio81/GoogleFileSearch.git
cd GoogleFileSearch

# Oppure scarica ZIP da GitHub e estrai in C:\GoogleFileSearch

# 2. Esegui setup automatico
.\setup\setup.bat

# 3. Configura credenziali
notepad .env
```

Nel file `.env`:
```env
GEMINI_API_KEY=la-tua-api-key
FILE_SEARCH_STORE_NAME=fileSearchStores/il-tuo-store-id
DEFAULT_MODEL=gemini-2.5-flash
```

### 2. Installazione come Servizio Windows

Usa **NSSM** (Non-Sucking Service Manager) per eseguire l'app come servizio Windows:

#### Installazione NSSM

```powershell
# Con Chocolatey
choco install nssm

# Oppure scarica manualmente da https://nssm.cc/download
# Estrai nssm.exe in C:\Windows\System32
```

#### Creazione Servizio

```powershell
# Apri PowerShell come Amministratore
cd C:\GoogleFileSearch

# Crea servizio
nssm install GoogleFileSearch "C:\GoogleFileSearch\venv\Scripts\python.exe" "C:\GoogleFileSearch\backend\app.py"

# Configura directory di lavoro
nssm set GoogleFileSearch AppDirectory "C:\GoogleFileSearch\backend"

# Configura descrizione
nssm set GoogleFileSearch Description "Google File Search RAG - Sistema di Gestione Documenti AI"

# Configura avvio automatico
nssm set GoogleFileSearch Start SERVICE_AUTO_START

# Configura output/error logs
nssm set GoogleFileSearch AppStdout "C:\GoogleFileSearch\logs\service-stdout.log"
nssm set GoogleFileSearch AppStderr "C:\GoogleFileSearch\logs\service-stderr.log"

# Avvia il servizio
nssm start GoogleFileSearch
```

#### Gestione Servizio

```powershell
# Verifica stato
nssm status GoogleFileSearch

# Avvia
nssm start GoogleFileSearch

# Ferma
nssm stop GoogleFileSearch

# Riavvia
nssm restart GoogleFileSearch

# Rimuovi servizio
nssm remove GoogleFileSearch confirm
```

### 3. Produzione con Waitress

**Waitress** è un WSGI server production-ready per Windows:

#### Installazione

```powershell
.\venv\Scripts\Activate.ps1
pip install waitress
```

#### Creazione Script di Avvio

Crea `setup\start-production.bat`:

```batch
@echo off
echo ========================================
echo AVVIO SERVER PRODUZIONE
echo ========================================
echo.

cd /d "%~dp0\.."

REM Verifica ambiente virtuale
if not exist "venv\" (
    echo ERRORE: Ambiente virtuale non trovato!
    pause
    exit /b 1
)

REM Verifica .env
if not exist ".env" (
    echo ERRORE: File .env non trovato!
    pause
    exit /b 1
)

REM Attiva ambiente virtuale
call venv\Scripts\activate.bat

echo Configurazione:
echo - Host: 0.0.0.0
echo - Port: 5000
echo - Threads: 4
echo - Timeout: 300s
echo.
echo Applicazione disponibile su:
echo - http://localhost:5000
echo - http://%COMPUTERNAME%:5000
echo.

REM Avvia con Waitress
cd backend
waitress-serve --host=0.0.0.0 --port=5000 --threads=4 --channel-timeout=300 --connection-limit=1000 app:app
```

#### Configurazione NSSM con Waitress

```powershell
# Crea servizio con Waitress
nssm install GoogleFileSearch "C:\GoogleFileSearch\venv\Scripts\waitress-serve.exe" "--host=0.0.0.0 --port=5000 --threads=4 --channel-timeout=300 app:app"
nssm set GoogleFileSearch AppDirectory "C:\GoogleFileSearch\backend"
nssm start GoogleFileSearch
```

### 4. Configurazione Firewall

```powershell
# Apri PowerShell come Amministratore

# Regola per porta 5000 (inbound)
New-NetFirewallRule -DisplayName "Google File Search - HTTP" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 5000 `
    -Action Allow `
    -Profile Domain,Private,Public

# Verifica regola
Get-NetFirewallRule -DisplayName "Google File Search*"
```

### 5. Reverse Proxy con IIS (Opzionale)

Per esporre l'app tramite IIS sulla porta 80/443:

#### Installazione Moduli IIS

1. Scarica e installa [URL Rewrite Module](https://www.iis.net/downloads/microsoft/url-rewrite)
2. Scarica e installa [Application Request Routing (ARR)](https://www.iis.net/downloads/microsoft/application-request-routing)

#### Abilita Proxy ARR

```powershell
# Apri IIS Manager
# Seleziona il server → Application Request Routing Cache
# Server Proxy Settings → Enable proxy → Apply
```

#### Configurazione web.config

Crea `C:\GoogleFileSearch\web.config`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <system.webServer>
        <rewrite>
            <rules>
                <rule name="ReverseProxyInboundRule" stopProcessing="true">
                    <match url="(.*)" />
                    <action type="Rewrite" url="http://localhost:5000/{R:1}" />
                    <serverVariables>
                        <set name="HTTP_X_FORWARDED_FOR" value="{REMOTE_ADDR}" />
                        <set name="HTTP_X_FORWARDED_PROTO" value="http" />
                    </serverVariables>
                </rule>
            </rules>
        </rewrite>
        
        <!-- Gestione Server-Sent Events (SSE) per streaming chat -->
        <httpProtocol>
            <customHeaders>
                <add name="X-Content-Type-Options" value="nosniff" />
            </customHeaders>
        </httpProtocol>
    </system.webServer>
</configuration>
```

#### Crea Sito IIS

```powershell
# PowerShell come Amministratore
Import-Module WebAdministration

# Crea sito
New-Website -Name "GoogleFileSearch" `
    -PhysicalPath "C:\GoogleFileSearch" `
    -Port 80 `
    -HostHeader "tuodominio.com"

# Avvia sito
Start-Website -Name "GoogleFileSearch"
```

### 6. SSL/HTTPS con IIS

```powershell
# Installa certificato SSL in IIS
# Certificate Manager → Import certificato
# IIS Manager → Sito → Bindings → Add HTTPS (porta 443)
# Seleziona certificato SSL
```

---

## 🐧 Linux Server

### 1. Setup Base

#### Requisiti
- Ubuntu 20.04+, Debian 11+, CentOS 8+
- Python 3.8+
- 1GB RAM minimo (2GB consigliato)
- 1GB spazio disco

#### Installazione

```bash
# 1. Aggiorna sistema
sudo apt update && sudo apt upgrade -y

# 2. Installa dipendenze
sudo apt install -y python3 python3-pip python3-venv git

# 3. Clona repository
git clone https://github.com/Attilio81/GoogleFileSearch.git
cd GoogleFileSearch

# 4. Esegui setup
chmod +x setup/setup.sh
./setup/setup.sh

# 5. Configura credenziali
nano .env
```

### 2. Installazione come Servizio Systemd

#### Crea File Servizio

```bash
sudo nano /etc/systemd/system/google-filesearch.service
```

Contenuto:

```ini
[Unit]
Description=Google File Search RAG - Sistema di Gestione Documenti AI
After=network.target

[Service]
Type=simple
User=tuo-utente
Group=tuo-gruppo
WorkingDirectory=/percorso/GoogleFileSearch
Environment="PATH=/percorso/GoogleFileSearch/venv/bin"
Environment="PYTHONUNBUFFERED=1"
ExecStart=/percorso/GoogleFileSearch/venv/bin/python3 /percorso/GoogleFileSearch/backend/app.py

# Restart automatico in caso di crash
Restart=always
RestartSec=10

# Limiti di sicurezza
PrivateTmp=true
NoNewPrivileges=true

# Logging
StandardOutput=append:/percorso/GoogleFileSearch/logs/service.log
StandardError=append:/percorso/GoogleFileSearch/logs/service-error.log

[Install]
WantedBy=multi-user.target
```

#### Attiva e Gestisci Servizio

```bash
# Ricarica configurazione systemd
sudo systemctl daemon-reload

# Abilita avvio automatico
sudo systemctl enable google-filesearch

# Avvia servizio
sudo systemctl start google-filesearch

# Verifica stato
sudo systemctl status google-filesearch

# Visualizza log
sudo journalctl -u google-filesearch -f

# Riavvia
sudo systemctl restart google-filesearch

# Ferma
sudo systemctl stop google-filesearch
```

### 3. Produzione con Gunicorn

**Gunicorn** è il WSGI server standard per Python su Linux:

#### Installazione

```bash
source venv/bin/activate
pip install gunicorn
```

#### Script di Avvio

File già presente: `setup/start-production.sh`

```bash
#!/bin/bash
cd "$(dirname "$0")/.."
source venv/bin/activate

gunicorn \
    --workers 4 \
    --bind 0.0.0.0:5000 \
    --timeout 120 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --log-level info \
    --chdir backend \
    app:app
```

#### Servizio Systemd con Gunicorn

Modifica `/etc/systemd/system/google-filesearch.service`:

```ini
[Service]
ExecStart=/percorso/GoogleFileSearch/venv/bin/gunicorn \
    --workers 4 \
    --bind 0.0.0.0:5000 \
    --timeout 120 \
    --access-logfile /percorso/GoogleFileSearch/logs/access.log \
    --error-logfile /percorso/GoogleFileSearch/logs/error.log \
    --chdir /percorso/GoogleFileSearch/backend \
    app:app
```

### 4. Reverse Proxy con Nginx

#### Installazione Nginx

```bash
sudo apt install nginx -y
```

#### Configurazione

```bash
sudo nano /etc/nginx/sites-available/google-filesearch
```

Contenuto:

```nginx
server {
    listen 80;
    server_name tuodominio.com www.tuodominio.com;
    
    # Redirect HTTP to HTTPS (opzionale, dopo SSL)
    # return 301 https://$server_name$request_uri;

    access_log /var/log/nginx/google-filesearch-access.log;
    error_log /var/log/nginx/google-filesearch-error.log;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeout per operazioni lunghe
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
        
        # Server-Sent Events (SSE) per streaming chat
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
    }

    # Static files (opzionale)
    location /static/ {
        alias /percorso/GoogleFileSearch/backend/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

#### Attiva Configurazione

```bash
# Crea link simbolico
sudo ln -s /etc/nginx/sites-available/google-filesearch /etc/nginx/sites-enabled/

# Verifica configurazione
sudo nginx -t

# Riavvia Nginx
sudo systemctl restart nginx
```

### 5. SSL/HTTPS con Certbot

```bash
# Installa Certbot
sudo apt install certbot python3-certbot-nginx -y

# Ottieni certificato SSL (Let's Encrypt)
sudo certbot --nginx -d tuodominio.com -d www.tuodominio.com

# Rinnovo automatico (già configurato)
sudo certbot renew --dry-run

# Certbot aggiorna automaticamente la configurazione Nginx
```

Configurazione HTTPS generata automaticamente:

```nginx
server {
    listen 443 ssl http2;
    server_name tuodominio.com www.tuodominio.com;

    ssl_certificate /etc/letsencrypt/live/tuodominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tuodominio.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # ... resto configurazione proxy
}
```

### 6. Firewall UFW

```bash
# Abilita firewall
sudo ufw enable

# Regole base
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https

# Porta backend (solo se esposta direttamente)
sudo ufw allow 5000/tcp

# Verifica regole
sudo ufw status
```

---

## 📊 Monitoraggio e Manutenzione

### Log Monitoring

**Windows:**
```powershell
# Visualizza log in tempo reale
Get-Content C:\GoogleFileSearch\logs\app.log -Wait -Tail 50

# Log servizio NSSM
Get-Content C:\GoogleFileSearch\logs\service-stdout.log -Wait
```

**Linux:**
```bash
# Log applicazione
tail -f /percorso/GoogleFileSearch/logs/app.log

# Log systemd
sudo journalctl -u google-filesearch -f

# Log Nginx
sudo tail -f /var/log/nginx/google-filesearch-access.log
sudo tail -f /var/log/nginx/google-filesearch-error.log

# Log Gunicorn
tail -f /percorso/GoogleFileSearch/logs/access.log
tail -f /percorso/GoogleFileSearch/logs/error.log
```

### Health Check

Crea script di monitoraggio:

**Windows** (`check-health.ps1`):
```powershell
$url = "http://localhost:5000/api/config"
try {
    $response = Invoke-WebRequest -Uri $url -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Servizio OK" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Servizio DOWN" -ForegroundColor Red
    # Riavvia servizio
    nssm restart GoogleFileSearch
}
```

**Linux** (`check-health.sh`):
```bash
#!/bin/bash
HEALTH_URL="http://localhost:5000/api/config"
if curl -sf "$HEALTH_URL" > /dev/null; then
    echo "✅ Servizio OK"
else
    echo "❌ Servizio DOWN - Riavvio..."
    sudo systemctl restart google-filesearch
fi
```

### Monitoraggio Risorse

```bash
# CPU e RAM utilizzate
top -p $(pgrep -f "python.*app.py")

# Con htop (più user-friendly)
sudo apt install htop -y
htop -p $(pgrep -f "python.*app.py")
```

---

## 💾 Backup e Disaster Recovery

### Backup Automatico

**Windows** (`backup.bat`):
```batch
@echo off
set BACKUP_DIR=C:\Backups\GoogleFileSearch
set DATE=%date:~-4%%date:~3,2%%date:~0,2%

mkdir "%BACKUP_DIR%" 2>nul
cd /d "C:\GoogleFileSearch"

echo [%date% %time%] Avvio backup...

REM Backup configurazione e documenti
tar -czf "%BACKUP_DIR%\backup-%DATE%.tar.gz" .env documents_storage logs

echo [%date% %time%] Backup completato: %BACKUP_DIR%\backup-%DATE%.tar.gz
```

**Linux** (`backup.sh`):
```bash
#!/bin/bash
BACKUP_DIR="/backup/google-filesearch"
DATE=$(date +%Y%m%d_%H%M%S)
PROJECT_DIR="/percorso/GoogleFileSearch"

mkdir -p "$BACKUP_DIR"

echo "[$(date)] Avvio backup..."

# Backup configurazione e documenti
tar -czf "$BACKUP_DIR/backup-$DATE.tar.gz" \
    -C "$PROJECT_DIR" \
    .env documents_storage logs

echo "[$(date)] Backup completato: $BACKUP_DIR/backup-$DATE.tar.gz"

# Pulizia backup vecchi (mantieni ultimi 7 giorni)
find "$BACKUP_DIR" -name "backup-*.tar.gz" -mtime +7 -delete
```

### Schedulazione Backup

**Windows (Task Scheduler):**
```powershell
$action = New-ScheduledTaskAction -Execute "C:\GoogleFileSearch\backup.bat"
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask -Action $action `
    -Trigger $trigger `
    -Principal $principal `
    -TaskName "GoogleFileSearch Backup" `
    -Description "Backup giornaliero Google File Search"
```

**Linux (Crontab):**
```bash
# Apri crontab
crontab -e

# Aggiungi backup giornaliero alle 2:00 AM
0 2 * * * /percorso/GoogleFileSearch/backup.sh >> /var/log/google-filesearch-backup.log 2>&1
```

### Restore da Backup

```bash
# Estrai backup
tar -xzf backup-20251118.tar.gz -C /percorso/GoogleFileSearch

# Riavvia servizio
# Windows:
nssm restart GoogleFileSearch

# Linux:
sudo systemctl restart google-filesearch
```

---

## 🔒 Sicurezza Best Practices

### 1. Protezione API Key

```bash
# Permessi restrittivi per .env
chmod 600 .env
```

### 2. Autenticazione (Opzionale ma Consigliato)

Aggiungi autenticazione Basic Auth in Nginx:

```bash
# Installa tool
sudo apt install apache2-utils -y

# Crea password file
sudo htpasswd -c /etc/nginx/.htpasswd admin

# Aggiungi in configurazione Nginx
location / {
    auth_basic "Restricted Access";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://localhost:5000;
    # ... resto configurazione
}
```

### 3. Rate Limiting

Configurato in `.env`:
```env
RATE_LIMIT_MAX=30
RATE_LIMIT_WINDOW=60
```

### 4. CORS Restrittivo

Modifica `backend/app.py` per limitare origini:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["https://tuodominio.com"])
```

### 5. Aggiornamenti Regolari

```bash
# Aggiorna sistema
sudo apt update && sudo apt upgrade -y

# Aggiorna dipendenze Python
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt --upgrade
```

### 6. Monitoraggio Accessi

Analizza log per tentativi di intrusione:

```bash
# Richieste sospette
sudo grep -i "401\|403\|404" /var/log/nginx/access.log | tail -100

# IP con troppe richieste
sudo awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -20
```

---

## 🔄 Aggiornamento in Produzione

### Procedura Zero-Downtime

```bash
# 1. Backup
./backup.sh

# 2. Scarica aggiornamenti
git pull origin main

# 3. Aggiorna dipendenze
source venv/bin/activate
pip install -r requirements.txt --upgrade

# 4. Test locale (opzionale)
cd backend
python app.py
# Verifica su http://localhost:5000
# Ctrl+C per fermare

# 5. Riavvia servizio
# Windows:
nssm restart GoogleFileSearch

# Linux:
sudo systemctl restart google-filesearch

# 6. Verifica
curl http://localhost:5000/api/config
```

---

## 📞 Supporto

Per problemi di deployment:
1. Controlla log: `logs/app.log`
2. Consulta [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. Apri issue su GitHub: https://github.com/Attilio81/GoogleFileSearch/issues

---

**Made with ❤️ for Production Deployments**
