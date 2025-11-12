@echo off
REM ========================================
REM Script di Installazione Automatica
REM Google File Search Application
REM ========================================

REM Vai alla root del progetto (cartella padre di setup/)
cd /d "%~dp0.."

echo.
echo ====================================
echo  INSTALLAZIONE GOOGLE FILE SEARCH
echo ====================================
echo.

REM Verifica Python
echo [1/5] Verifica Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRORE: Python non trovato!
    echo Installa Python 3.8+ da https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo.

REM Crea ambiente virtuale
echo [2/5] Creazione ambiente virtuale...
if exist venv (
    echo Ambiente virtuale gia' esistente, lo rimuovo...
    rmdir /s /q venv
)
python -m venv venv
if errorlevel 1 (
    echo ERRORE: Impossibile creare l'ambiente virtuale
    pause
    exit /b 1
)
echo Ambiente virtuale creato con successo!
echo.

REM Attiva ambiente virtuale
echo [3/5] Attivazione ambiente virtuale...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERRORE: Impossibile attivare l'ambiente virtuale
    pause
    exit /b 1
)
echo.

REM Installa dipendenze
echo [4/5] Installazione dipendenze...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERRORE: Installazione dipendenze fallita
    pause
    exit /b 1
)
echo.

REM Verifica file .env
echo [5/5] Verifica configurazione...
if not exist .env (
    echo.
    echo ATTENZIONE: File .env non trovato!
    echo.
    if exist .env.example (
        echo Copio .env.example in .env...
        copy .env.example .env
        echo.
        echo IMPORTANTE: Modifica il file .env con le tue credenziali:
        echo - GEMINI_API_KEY=la-tua-api-key
        echo - FILE_SEARCH_STORE_NAME=il-tuo-store-name
        echo.
        notepad .env
    ) else (
        echo Creo file .env di esempio...
        (
            echo # Configurazione Google File Search
            echo GEMINI_API_KEY=your-api-key-here
            echo FILE_SEARCH_STORE_NAME=fileSearchStores/your-store-id
            echo DEFAULT_MODEL=gemini-2.5-pro
            echo CHUNK_SIZE=512
            echo CHUNK_OVERLAP_PERCENT=10
        ) > .env
        echo.
        echo File .env creato. Aprilo e inserisci le tue credenziali.
        echo.
        notepad .env
    )
) else (
    echo File .env trovato!
)
echo.

REM Crea store (opzionale)
echo.
echo Vuoi creare un nuovo File Search Store? (s/n)
choice /c sn /n /m "Scelta: "
if errorlevel 2 goto skip_store
if errorlevel 1 goto create_store

:create_store
echo.
echo Creazione File Search Store...
cd backend
python create_store.py
cd ..
goto end_setup

:skip_store
echo Store non creato. Puoi crearlo in seguito con: python backend\create_store.py
echo.

:end_setup
echo.
echo ====================================
echo  INSTALLAZIONE COMPLETATA!
echo ====================================
echo.
echo Per avviare l'applicazione usa: start.bat
echo.
pause
