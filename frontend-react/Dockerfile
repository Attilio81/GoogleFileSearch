# Dockerfile per Frontend React - Multi-stage build

# Stage 1: Build dell'applicazione React
FROM node:20-alpine AS builder

# Imposta la directory di lavoro
WORKDIR /app

# Copia i file di configurazione delle dipendenze
COPY package*.json ./

# Installa le dipendenze
RUN npm ci --only=production=false

# Copia tutto il codice sorgente
COPY . .

# Build dell'applicazione per produzione
RUN npm run build

# Stage 2: Serve dell'applicazione con Nginx
FROM nginx:alpine

# Copia i file buildati dallo stage precedente
COPY --from=builder /app/dist /usr/share/nginx/html

# Copia la configurazione personalizzata di Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Esponi la porta 80
EXPOSE 80

# Comando per avviare Nginx
CMD ["nginx", "-g", "daemon off;"]
