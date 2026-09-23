PYTHON ?= python

.PHONY: test lint validate case 

test:
	$(PYTHON) -m pytest -q

lint:
	ruff check .

validate:
	$(PYTHON) tools/validate_registry.py

case:
	PYTHONPATH=src $(PYTHON) -m cases.case_001_highpass_01_vs_1hz.run --subjects 1
