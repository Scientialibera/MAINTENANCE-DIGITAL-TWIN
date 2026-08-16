.PHONY: install test lint run data train no-emoji docker

install:
	python -m pip install -e ".[dev]"

test:
	pytest -q

lint:
	ruff check api domain services ml optimization scripts tests

run:
	uvicorn api.main:app --reload --port 8000

data:
	python scripts/fetch_nasa_data.py --cmapss

train:
	python scripts/train_rul_model.py

no-emoji:
	python scripts/check_no_emoji.py

docker:
	docker build -t maintenance-digital-twin .
