@echo off
REM ========================================
REM Script di Avvio Rapido
REM Google File Search Application
REM ========================================

echo.
echo ====================================
echo  AVVIO GOOGLE FILE SEARCH
echo ====================================
echo.

REM Verifica ambiente virtuale
if not exist venv (
    echo ERRORE: Ambiente virtuale non trovato!
    echo Esegui prima setup.bat per installare l'applicazione.
    pause
    exit /b 1
)

REM Verifica file .env
if not exist .env (
    echo ERRORE: File .env non trovato!
    echo Configura il file .env con le tue credenziali.
    pause
    exit /b 1
)

REM Attiva ambiente virtuale
echo Attivazione ambiente virtuale...
call venv\Scripts\activate.bat

REM Avvia applicazione
echo.
echo Avvio server Flask...
echo.
echo Applicazione disponibile su:
echo - Admin Interface: http://localhost:5000
echo - Chat Interface:  http://localhost:5000/chat
echo - Chunks Viewer:   http://localhost:5000/chunks
echo.
echo Premi CTRL+C per fermare il server
echo.
echo ====================================
echo.

cd backend
python app.py

pause
