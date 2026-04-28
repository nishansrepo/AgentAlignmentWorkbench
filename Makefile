.PHONY: install setup-model inject app clean help
install:
	pip install -r requirements.txt
setup-model:
	ollama pull qwen3:8b
inject:
	python inject_ml_ta.py
app:
	streamlit run src/app/app.py --server.port 8501
clean:
	rm -rf sessions/*.json uploads/* data/*
help:
	@grep -E '^[a-zA-Z_-]+:' Makefile | sed 's/:.*//'
.DEFAULT_GOAL := help
