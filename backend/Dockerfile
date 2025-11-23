# Dockerfile per Backend Flask
FROM python:3.11-slim

# Imposta la directory di lavoro
WORKDIR /app

# Installa le dipendenze di sistema necessarie
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia il file requirements.txt dalla root del progetto
COPY requirements.txt .

# Installa le dipendenze Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il codice del backend
COPY backend/ .

# Crea directory per upload temporanei
RUN mkdir -p /app/uploads && chmod 777 /app/uploads

# Esponi la porta Flask
EXPOSE 5000

# Variabili d'ambiente predefinite (possono essere sovrascritte)
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Comando per avviare l'applicazione con gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
