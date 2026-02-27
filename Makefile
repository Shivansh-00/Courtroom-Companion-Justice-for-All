.PHONY: up down lint test pycheck

up:
	docker compose up --build

down:
	docker compose down -v

pycheck:
	python -m py_compile services/api-gateway/app/main.py \
	 services/user-service/app/main.py \
	 services/document-service/app/main.py \
	 services/nlp-service/app/main.py \
	 services/prediction-service/app/main.py \
	 services/blockchain-service/app/main.py \
	 services/notification-service/app/main.py \
	 services/matchmaking-service/app/main.py

test: pycheck
