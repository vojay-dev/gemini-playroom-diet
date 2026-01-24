.PHONY: all
all:
	@echo "See README.md"

# Starts local frontend, backend, and Airflow services, talks to prod DB and storage
.PHONY: start
start:
	bin/start
