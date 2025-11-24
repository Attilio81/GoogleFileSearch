# Build Stage
FROM node:18-alpine as build

WORKDIR /app

# Copia i file di configurazione delle dipendenze
COPY package*.json ./

# Installa le dipendenze
RUN npm ci

# Copia il codice sorgente
COPY . .

# Costruisci l'applicazione
RUN npm run build

# Production Stage
FROM nginx:alpine

# Copia i file costruiti dalla fase di build
COPY --from=build /app/dist /usr/share/nginx/html

# Copia la configurazione custom di Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Esponi la porta 80
EXPOSE 80

# Avvia Nginx
CMD ["nginx", "-g", "daemon off;"]
