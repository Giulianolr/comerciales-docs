.PHONY: help install dev test lint format migrate seed serve build deploy clean logs shell

# Variables
PYTHON := python3
UV := uv
BACKEND_DIR := comerciales-backend
FRONTEND_DIR := frontend-code
INFRA_DIR := comerciales-infra
VENV := .venv
BLACK := $(UV) run black
PYTEST := $(UV) run pytest
ALEMBIC := $(UV) run alembic
DOCKER := docker
DOCKER_COMPOSE := docker-compose

# Colors
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

.DEFAULT_GOAL := help

##@ General

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(BLUE)%-20s$(NC) %s\n", $$1, $$2}'

status: ## Show project status (git, python, node versions)
	@echo "$(BLUE)=== Project Status ===$(NC)"
	@git status --short
	@echo "\n$(BLUE)Python version:$(NC)"
	@$(PYTHON) --version
	@echo "\n$(BLUE)UV version:$(NC)"
	@$(UV) --version
	@echo "\n$(BLUE)Current branch:$(NC)"
	@git branch --show-current

##@ Backend Setup & Dependencies

backend-install: ## Install backend dependencies (uv)
	@echo "$(BLUE)Installing backend dependencies...$(NC)"
	cd $(BACKEND_DIR) && $(UV) sync

backend-freeze: ## Freeze backend dependencies to requirements.txt
	@echo "$(BLUE)Freezing backend dependencies...$(NC)"
	cd $(BACKEND_DIR) && $(UV) lock

backend-update: ## Update backend dependencies
	@echo "$(BLUE)Updating backend dependencies...$(NC)"
	cd $(BACKEND_DIR) && $(UV) sync --upgrade

##@ Backend Development

backend-dev: ## Run backend in development mode (with hot reload)
	@echo "$(BLUE)Starting backend dev server...$(NC)"
	cd $(BACKEND_DIR) && $(UV) run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

backend-shell: ## Open Python shell with backend context
	@echo "$(BLUE)Opening backend shell...$(NC)"
	cd $(BACKEND_DIR) && $(UV) run python

backend-format: ## Format backend code (Black)
	@echo "$(BLUE)Formatting backend code...$(NC)"
	cd $(BACKEND_DIR) && $(BLACK) app tests

backend-lint: ## Lint backend code (Ruff)
	@echo "$(BLUE)Linting backend code...$(NC)"
	cd $(BACKEND_DIR) && $(UV) run ruff check app tests --fix

backend-type-check: ## Type check backend code (Mypy)
	@echo "$(BLUE)Type checking backend code...$(NC)"
	cd $(BACKEND_DIR) && $(UV) run mypy app

##@ Backend Testing

test: backend-test ## Run all backend tests (alias)

backend-test: ## Run all backend tests with strict TDD mode
	@echo "$(BLUE)Running backend tests...$(NC)"
	cd $(BACKEND_DIR) && $(PYTEST) tests/ -v --tb=short

backend-test-unit: ## Run only unit tests
	@echo "$(BLUE)Running unit tests...$(NC)"
	cd $(BACKEND_DIR) && $(PYTEST) tests/unit/ -v --tb=short

backend-test-integration: ## Run only integration tests
	@echo "$(BLUE)Running integration tests...$(NC)"
	cd $(BACKEND_DIR) && $(PYTEST) tests/integration/ -v --tb=short

backend-test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	cd $(BACKEND_DIR) && $(PYTEST) tests/ --cov=app --cov-report=html --cov-report=term

backend-test-watch: ## Run tests in watch mode (requires pytest-watch)
	@echo "$(BLUE)Running tests in watch mode...$(NC)"
	cd $(BACKEND_DIR) && $(UV) run ptw tests/ -- -v

##@ Database Migrations & Seeding

migrate: ## Run pending database migrations
	@echo "$(BLUE)Running migrations...$(NC)"
	cd $(BACKEND_DIR) && $(ALEMBIC) upgrade head

migrate-create: ## Create a new migration (usage: make migrate-create name=my_migration)
	@echo "$(BLUE)Creating migration: $(name)...$(NC)"
	cd $(BACKEND_DIR) && $(ALEMBIC) revision --autogenerate -m "$(name)"

migrate-down: ## Rollback one migration
	@echo "$(YELLOW)Rolling back one migration...$(NC)"
	cd $(BACKEND_DIR) && $(ALEMBIC) downgrade -1

migrate-history: ## Show migration history
	@echo "$(BLUE)Migration history:$(NC)"
	cd $(BACKEND_DIR) && $(ALEMBIC) history

db-init: migrate ## Initialize database schema (run migrations)
	@echo "$(GREEN)Database initialized$(NC)"

db-seed: ## Seed database with test data
	@echo "$(BLUE)Seeding database...$(NC)"
	cd $(BACKEND_DIR) && $(UV) run python -m scripts.seed_data

db-reset: ## Reset database (DROP + migrations + seed)
	@echo "$(RED)Resetting database...$(NC)"
	cd $(BACKEND_DIR) && $(ALEMBIC) downgrade base
	@make db-init
	@make db-seed
	@echo "$(GREEN)Database reset complete$(NC)"

db-clean: ## Drop all tables (DESTRUCTIVE)
	@echo "$(RED)Dropping all tables...$(NC)"
	cd $(BACKEND_DIR) && $(UV) run python -c "from app.database import engine; from app.models import Base; Base.metadata.drop_all(engine)"

##@ Frontend Setup & Development

frontend-install: ## Install frontend dependencies (npm/yarn)
	@echo "$(BLUE)Installing frontend dependencies...$(NC)"
	cd $(FRONTEND_DIR) && npm install

frontend-dev: ## Run frontend dev server
	@echo "$(BLUE)Starting frontend dev server...$(NC)"
	cd $(FRONTEND_DIR) && npm run dev

frontend-build: ## Build frontend for production
	@echo "$(BLUE)Building frontend...$(NC)"
	cd $(FRONTEND_DIR) && npm run build

frontend-preview: ## Preview production build locally
	@echo "$(BLUE)Previewing production build...$(NC)"
	cd $(FRONTEND_DIR) && npm run preview

frontend-lint: ## Lint frontend code
	@echo "$(BLUE)Linting frontend code...$(NC)"
	cd $(FRONTEND_DIR) && npm run lint

frontend-format: ## Format frontend code (Prettier)
	@echo "$(BLUE)Formatting frontend code...$(NC)"
	cd $(FRONTEND_DIR) && npm run format

frontend-test: ## Run frontend tests
	@echo "$(BLUE)Running frontend tests...$(NC)"
	cd $(FRONTEND_DIR) && npm run test

##@ Docker & Containerization

docker-build: ## Build Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	$(DOCKER_COMPOSE) build

docker-up: ## Start containers (docker-compose up)
	@echo "$(BLUE)Starting containers...$(NC)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)Containers started$(NC)"
	@make logs

docker-down: ## Stop containers (docker-compose down)
	@echo "$(YELLOW)Stopping containers...$(NC)"
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)Containers stopped$(NC)"

docker-logs: logs ## Show Docker logs (alias)

docker-shell: ## Open shell in running backend container
	@echo "$(BLUE)Opening shell in backend container...$(NC)"
	$(DOCKER_COMPOSE) exec backend sh

docker-restart: ## Restart containers
	@echo "$(YELLOW)Restarting containers...$(NC)"
	$(DOCKER_COMPOSE) restart
	@echo "$(GREEN)Containers restarted$(NC)"

##@ Deployment

deploy: deploy-staging ## Deploy to staging (default)

deploy-staging: ## Deploy to staging environment
	@echo "$(BLUE)Deploying to staging...$(NC)"
	@echo "Building images..."
	@make docker-build
	@echo "Running migrations..."
	@make migrate
	@echo "$(GREEN)Staging deployment complete$(NC)"

deploy-prod: ## Deploy to production
	@echo "$(RED)!!! PRODUCTION DEPLOYMENT !!!$(NC)"
	@echo "$(YELLOW)This will deploy to production. Press Ctrl+C to cancel.$(NC)"
	@sleep 3
	@echo "$(BLUE)Deploying to production...$(NC)"
	@echo "Building images..."
	@make docker-build
	@echo "Running migrations..."
	@make migrate
	@echo "$(GREEN)Production deployment complete$(NC)"

deploy-rollback: ## Rollback to previous deployment
	@echo "$(YELLOW)Rolling back to previous deployment...$(NC)"
	@make migrate-down
	@echo "$(GREEN)Rollback complete$(NC)"

##@ Logs & Debugging

logs: ## Show Docker logs (all services)
	@echo "$(BLUE)Showing logs...$(NC)"
	@$(DOCKER_COMPOSE) logs -f --tail=50

logs-backend: ## Show backend logs only
	@$(DOCKER_COMPOSE) logs -f --tail=50 backend

logs-db: ## Show database logs only
	@$(DOCKER_COMPOSE) logs -f --tail=50 db

logs-clear: ## Clear all Docker logs
	@echo "$(YELLOW)Clearing logs...$(NC)"
	@$(DOCKER_COMPOSE) logs --timestamps | wc -l
	@echo "$(GREEN)Logs cleared$(NC)"

##@ Code Quality & Cleanup

format: ## Format all code (backend + frontend)
	@make backend-format
	@make frontend-format
	@echo "$(GREEN)Code formatted$(NC)"

lint: ## Lint all code (backend + frontend)
	@make backend-lint
	@make frontend-lint
	@echo "$(GREEN)All code linted$(NC)"

quality: format lint backend-type-check ## Run all quality checks
	@echo "$(GREEN)Code quality checks complete$(NC)"

clean: ## Clean build artifacts and cache
	@echo "$(YELLOW)Cleaning build artifacts...$(NC)"
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	cd $(FRONTEND_DIR) && rm -rf node_modules .next build 2>/dev/null || true
	@echo "$(GREEN)Cleanup complete$(NC)"

clean-all: clean ## Clean everything including dependencies
	@echo "$(RED)Removing all dependencies...$(NC)"
	cd $(BACKEND_DIR) && rm -rf .venv __pycache__ 2>/dev/null || true
	cd $(FRONTEND_DIR) && rm -rf node_modules 2>/dev/null || true
	$(DOCKER_COMPOSE) down -v
	@echo "$(GREEN)Full cleanup complete$(NC)"

##@ Development Workflow

install: backend-install frontend-install db-init ## Complete project setup
	@echo "$(GREEN)Project setup complete!$(NC)"
	@echo "Run '$(BLUE)make dev$(NC)' to start development"

dev: ## Start full development environment (backend + frontend)
	@echo "$(BLUE)Starting development environment...$(NC)"
	@echo "Backend will run on http://localhost:8000"
	@echo "Frontend will run on http://localhost:3000"
	@echo "API docs at http://localhost:8000/docs"
	@echo ""
	@make backend-dev & make frontend-dev

dev-docker: ## Start development environment with Docker
	@echo "$(BLUE)Starting Docker development environment...$(NC)"
	@make docker-build
	@make docker-up
	@make migrate
	@make logs

##@ Database

db-shell: ## Open database shell (psql)
	@echo "$(BLUE)Opening database shell...$(NC)"
	$(DOCKER_COMPOSE) exec db psql -U postgres -d comerciales

db-backup: ## Backup database
	@echo "$(BLUE)Backing up database...$(NC)"
	@mkdir -p backups
	@$(DOCKER_COMPOSE) exec db pg_dump -U postgres comerciales > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)Backup complete$(NC)"

db-restore: ## Restore database from backup (usage: make db-restore file=backups/backup_20260421_120000.sql)
	@echo "$(BLUE)Restoring database from $(file)...$(NC)"
	@$(DOCKER_COMPOSE) exec -T db psql -U postgres comerciales < $(file)
	@echo "$(GREEN)Restore complete$(NC)"

##@ Utilities

check-deps: ## Check if all required tools are installed
	@echo "$(BLUE)Checking dependencies...$(NC)"
	@command -v python3 >/dev/null 2>&1 && echo "$(GREEN)✓$(NC) Python3" || echo "$(RED)✗$(NC) Python3"
	@command -v $(UV) >/dev/null 2>&1 && echo "$(GREEN)✓$(NC) UV" || echo "$(RED)✗$(NC) UV"
	@command -v docker >/dev/null 2>&1 && echo "$(GREEN)✓$(NC) Docker" || echo "$(RED)✗$(NC) Docker"
	@command -v docker-compose >/dev/null 2>&1 && echo "$(GREEN)✓$(NC) Docker Compose" || echo "$(RED)✗$(NC) Docker Compose"
	@command -v npm >/dev/null 2>&1 && echo "$(GREEN)✓$(NC) NPM" || echo "$(RED)✗$(NC) NPM"
	@command -v git >/dev/null 2>&1 && echo "$(GREEN)✓$(NC) Git" || echo "$(RED)✗$(NC) Git"

version: ## Show versions of key tools
	@echo "$(BLUE)Tool versions:$(NC)"
	@python3 --version
	@$(UV) --version
	@docker --version
	@docker-compose --version
	@npm --version
	@git --version

info: ## Show project info
	@echo "$(BLUE)=== Proyecto Locales Comerciales ===$(NC)"
	@echo "$(BLUE)Backend:$(NC) FastAPI + SQLAlchemy + Alembic"
	@echo "$(BLUE)Frontend:$(NC) React/Next.js"
	@echo "$(BLUE)Database:$(NC) PostgreSQL"
	@echo "$(BLUE)Infrastructure:$(NC) Docker + Hetzner VPS"
	@echo "$(BLUE)Testing:$(NC) Pytest (strict TDD mode)"
	@echo ""
	@echo "$(BLUE)Quick Start:$(NC)"
	@echo "  1. $(GREEN)make install$(NC)       - Install everything"
	@echo "  2. $(GREEN)make dev$(NC)           - Start development (backend + frontend)"
	@echo "  3. $(GREEN)make test$(NC)          - Run tests"
	@echo ""
	@echo "$(BLUE)More info:$(NC) make help"
