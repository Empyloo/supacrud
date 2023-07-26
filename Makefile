test:
	@echo "Running tests..."
	@if [ -z "$$file" ]; then \
		pytest tests --cov=supacrud; \
	else \
		pytest tests/$$file --cov=supacrud; \
	fi

PHONY: install
install:
	pip install --upgrade pip
	pip install -r requirements.txt
