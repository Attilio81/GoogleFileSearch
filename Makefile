.PHONY: help build up down restart logs logs-backend logs-frontend shell-backend shell-frontend clean test dev

# Colori per output
GREEN  := \033[0;32m
YELLOW := \033[0;33m
RED    := \033[0;31m
RESET  := \033[0m

help: ## Mostra questo messaggio di aiuto
	@echo "$(GREEN)Google File Search - Docker Commands$(RESET)"
	@echo ""
	@echo "$(YELLOW)Comandi disponibili:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Esempi:$(RESET)"
	@echo "  make setup     - Prima installazione"
	@echo "  make up        - Avvia l'applicazione"
	@echo "  make logs      - Visualizza i logs"
	@echo "  make down      - Ferma l'applicazione"

setup: ## Prima installazione: crea .env e builda i container
	@echo "$(GREEN)Setup iniziale...$(RESET)"
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)Creazione file .env da .env.docker.example...$(RESET)"; \
		cp .env.docker.example .env; \
		echo "$(RED)IMPORTANTE: Modifica il file .env con i tuoi valori!$(RESET)"; \
	else \
		echo "$(YELLOW)File .env già esistente, skip...$(RESET)"; \
	fi
	@echo "$(GREEN)Build dei container...$(RESET)"
	@docker-compose build
	@echo "$(GREEN)Setup completato!$(RESET)"
	@echo "$(YELLOW)Ricorda di configurare GEMINI_API_KEY in .env$(RESET)"

build: ## Build dei container Docker
	@echo "$(GREEN)Building containers...$(RESET)"
	@docker-compose build

build-nc: ## Build dei container senza cache
	@echo "$(GREEN)Building containers (no cache)...$(RESET)"
	@docker-compose build --no-cache

up: ## Avvia l'applicazione (detached mode)
	@echo "$(GREEN)Starting containers...$(RESET)"
	@docker-compose up -d
	@echo "$(GREEN)Applicazione avviata!$(RESET)"
	@echo "$(YELLOW)Frontend: http://localhost$(RESET)"
	@echo "$(YELLOW)Backend:  http://localhost:5000$(RESET)"
	@echo "$(YELLOW)Logs:     make logs$(RESET)"

up-build: ## Avvia l'applicazione con rebuild
	@echo "$(GREEN)Starting containers with rebuild...$(RESET)"
	@docker-compose up -d --build

down: ## Ferma e rimuove i container
	@echo "$(YELLOW)Stopping containers...$(RESET)"
	@docker-compose down

down-v: ## Ferma e rimuove i container + volumi
	@echo "$(RED)Stopping containers and removing volumes...$(RESET)"
	@docker-compose down -v

restart: ## Restart dei container
	@echo "$(YELLOW)Restarting containers...$(RESET)"
	@docker-compose restart

restart-backend: ## Restart solo backend
	@echo "$(YELLOW)Restarting backend...$(RESET)"
	@docker-compose restart backend

restart-frontend: ## Restart solo frontend
	@echo "$(YELLOW)Restarting frontend...$(RESET)"
	@docker-compose restart frontend

logs: ## Visualizza i logs di tutti i servizi
	@docker-compose logs -f

logs-backend: ## Visualizza i logs del backend
	@docker-compose logs -f backend

logs-frontend: ## Visualizza i logs del frontend
	@docker-compose logs -f frontend

ps: ## Mostra lo stato dei container
	@docker-compose ps

shell-backend: ## Apri una shell nel container backend
	@docker-compose exec backend /bin/bash

shell-frontend: ## Apri una shell nel container frontend
	@docker-compose exec frontend /bin/sh

test-api: ## Testa l'API del backend
	@echo "$(GREEN)Testing backend API...$(RESET)"
	@docker-compose exec backend python test_api.py

test-backend: ## Esegui i test del backend
	@echo "$(GREEN)Running backend tests...$(RESET)"
	@docker-compose exec backend pytest tests/ -v

health: ## Verifica lo stato di salute dei servizi
	@echo "$(GREEN)Health check...$(RESET)"
	@echo "$(YELLOW)Backend:$(RESET)"
	@curl -s http://localhost:5000/api/config > /dev/null && echo "  $(GREEN)✓ Backend OK$(RESET)" || echo "  $(RED)✗ Backend DOWN$(RESET)"
	@echo "$(YELLOW)Frontend:$(RESET)"
	@curl -s http://localhost > /dev/null && echo "  $(GREEN)✓ Frontend OK$(RESET)" || echo "  $(RED)✗ Frontend DOWN$(RESET)"

clean: ## Pulizia completa: ferma tutto e rimuove immagini
	@echo "$(RED)Cleaning up...$(RESET)"
	@docker-compose down -v --rmi all
	@echo "$(GREEN)Cleanup completato!$(RESET)"

dev: ## Avvia in modalità development con hot reload
	@echo "$(GREEN)Starting in development mode...$(RESET)"
	@docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

dev-build: ## Build e avvia in modalità development
	@echo "$(GREEN)Building and starting in development mode...$(RESET)"
	@docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

prune: ## Pulizia Docker system (attenzione!)
	@echo "$(RED)Pruning Docker system...$(RESET)"
	@docker system prune -a --volumes

backup: ## Backup del volume uploads
	@echo "$(GREEN)Creating backup...$(RESET)"
	@docker run --rm -v googlefilesearch_uploads_data:/data \
		-v $$(pwd):/backup alpine tar czf /backup/uploads-backup-$$(date +%Y%m%d-%H%M%S).tar.gz /data
	@echo "$(GREEN)Backup completato!$(RESET)"

stats: ## Mostra statistiche di utilizzo risorse
	@docker stats --no-stream

# Default target
.DEFAULT_GOAL := help
