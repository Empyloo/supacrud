PHONY: test install
test:
	@echo "Running tests..."
	@if [ -z "$$file" ]; then \
		pytest tests --cov=supacrud; \
	else \
		pytest tests/$$file --cov=supacrud; \
	fi

install:
	pip install --upgrade pip
	pip install -r requirements.txt

e2e:
	python scripts/local_supabase_runner.py
