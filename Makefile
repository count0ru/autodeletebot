# Auto-Delete Telegram Bot Makefile
# Make sure to use tabs for indentation (not spaces)

.PHONY: help deps deps-tests tests build lint clean

# Default target
help:
	@echo "Auto-Delete Telegram Bot - Available targets:"
	@echo ""
	@echo "  deps        - Install virtual environment and main requirements"
	@echo "  deps-tests  - Install virtual environment and all requirements (including tests)"
	@echo "  tests       - Run all tests"
	@echo "  build       - Build Docker container"
	@echo "  lint        - Run pylint code analysis"
	@echo "  clean       - Clean up generated files and virtual environment"
	@echo "  help        - Show this help message"
	@echo ""

# Install virtual environment and main requirements
deps:
	@echo "🐍 Creating Python virtual environment..."
	python3 -m venv venv
	@echo "📦 Installing main requirements..."
	venv/bin/python3 -m pip install --upgrade pip
	venv/bin/python3 -m pip install -r requirements.txt
	@echo "✅ Dependencies installed successfully!"

# Install virtual environment and all requirements (including tests)
deps-tests: deps
	@echo "🧪 Installing test requirements..."
	venv/bin/python3 -m pip install -r requirements-test.txt
	@echo "✅ Test dependencies installed successfully!"

# Run all tests
tests:
	@echo "🧪 Running tests..."
	@if [ ! -d "venv" ]; then \
		echo "❌ Virtual environment not found. Run 'make deps-tests' first."; \
		exit 1; \
	fi
	venv/bin/python3 -m pytest tests/ -v --tb=short
	@echo "✅ Tests completed!"

# Run tests with coverage
tests-cov:
	@echo "🧪 Running tests with coverage..."
	@if [ ! -d "venv" ]; then \
		echo "❌ Virtual environment not found. Run 'make deps-tests' first."; \
		exit 1; \
	fi
	venv/bin/python3 -m pytest tests/ --cov=. --cov-report=html --cov-report=term
	@echo "✅ Coverage report generated in htmlcov/ directory!"

# Run specific test file
test-file:
	@echo "🧪 Running specific test file..."
	@if [ ! -d "venv" ]; then \
		echo "❌ Virtual environment not found. Run 'make deps-tests' first."; \
		exit 1; \
	fi
	@if [ -z "$(FILE)" ]; then \
		echo "❌ Please specify FILE=path/to/test.py"; \
		echo "Example: make test-file FILE=tests/test_database.py"; \
		exit 1; \
	fi
	venv/bin/python3 -m pytest $(FILE) -v

# Build Docker container
build:
	@echo "🐳 Building Docker container..."
	@if [ ! -f "Dockerfile" ]; then \
		echo "❌ Dockerfile not found. Creating basic Dockerfile..."; \
		echo "FROM python:3.11-slim" > Dockerfile; \
		echo "WORKDIR /app" >> Dockerfile; \
		echo "COPY requirements.txt ." >> Dockerfile; \
		echo "RUN pip install -r requirements.txt" >> Dockerfile; \
		echo "COPY . ." >> Dockerfile; \
		echo "CMD [\"python3\", \"telegram_bot.py\"]" >> Dockerfile; \
	fi
	docker build -t autodeletebot:latest .
	@echo "✅ Docker container built successfully!"
	@echo "Run with: docker run -d --name autodeletebot autodeletebot:latest"

# Run pylint code analysis
lint:
	@echo "🔍 Running pylint code analysis..."
	@if [ ! -d "venv" ]; then \
		echo "❌ Virtual environment not found. Run 'make deps' first."; \
		exit 1; \
	fi
	@if [ ! -f ".pylintrc" ]; then \
		echo "❌ .pylintrc not found. Creating default configuration..."; \
		echo "[MASTER]" > .pylintrc; \
		echo "jobs=0" >> .pylintrc; \
		echo "" >> .pylintrc; \
		echo "[MESSAGES CONTROL]" >> .pylintrc; \
		echo "disable=W0718,C0114" >> .pylintrc; \
		echo "" >> .pylintrc; \
		echo "[FORMAT]" >> .pylintrc; \
		echo "max-line-length=120" >> .pylintrc; \
	fi
	venv/bin/python3 -m pylint --rcfile .pylintrc *.py
	@echo "✅ Linting completed!"

# Run specific linting tool
lint-flake8:
	@echo "🔍 Running flake8..."
	@if [ ! -d "venv" ]; then \
		echo "❌ Virtual environment not found. Run 'make deps' first."; \
		exit 1; \
	fi
	@if ! venv/bin/python3 -m pip show flake8 > /dev/null 2>&1; then \
		echo "📦 Installing flake8..."; \
		venv/bin/python3 -m pip install flake8; \
	fi
	venv/bin/python3 -m flake8 *.py --max-line-length=120 --ignore=E501,W503

# Run black code formatter
format:
	@echo "🎨 Running black code formatter..."
	@if [ ! -d "venv" ]; then \
		echo "❌ Virtual environment not found. Run 'make deps' first."; \
		exit 1; \
	fi
	@if ! venv/bin/python3 -m pip show black > /dev/null 2>&1; then \
		echo "📦 Installing black..."; \
		venv/bin/python3 -m pip install black; \
	fi
	venv/bin/python3 -m black *.py --line-length=120

# Clean up generated files and virtual environment
clean:
	@echo "🧹 Cleaning up..."
	@if [ -d "venv" ]; then \
		echo "Removing virtual environment..."; \
		rm -rf venv; \
	fi
	@if [ -d "__pycache__" ]; then \
		echo "Removing Python cache..."; \
		rm -rf __pycache__; \
	fi
	@if [ -d ".pytest_cache" ]; then \
		echo "Removing pytest cache..."; \
		rm -rf .pytest_cache; \
	fi
	@if [ -d "htmlcov" ]; then \
		echo "Removing coverage reports..."; \
		rm -rf htmlcov; \
	fi
	@if [ -d ".coverage" ]; then \
		echo "Removing coverage data..."; \
		rm -f .coverage; \
	fi
	@if [ -f "*.pyc" ]; then \
		echo "Removing Python bytecode..."; \
		rm -f *.pyc; \
	fi
	@echo "✅ Cleanup completed!"

# Install development tools
dev-tools:
	@echo "🛠️ Installing development tools..."
	@if [ ! -d "venv" ]; then \
		echo "❌ Virtual environment not found. Run 'make deps' first."; \
		exit 1; \
	fi
	venv/bin/python3 -m pip install black flake8 mypy pre-commit
	@echo "✅ Development tools installed!"

# Run all checks (lint + tests)
check: lint tests
	@echo "✅ All checks completed successfully!"

# Quick setup for development
setup: deps-tests dev-tools
	@echo "🚀 Development environment ready!"
	@echo "Available commands:"
	@echo "  make tests     - Run tests"
	@echo "  make lint      - Run linting"
	@echo "  make format    - Format code"
	@echo "  make check     - Run all checks"
