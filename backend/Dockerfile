# Usa un'immagine base di Python leggera
FROM python:3.9-slim

# Imposta la directory di lavoro nel container
WORKDIR /app

# Copia i file dei requisiti
COPY ../requirements.txt .

# Installa le dipendenze
RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice del backend
COPY . .

# Esponi la porta su cui gira Flask
EXPOSE 5000

# Comando per avviare l'applicazione con Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
