
PYTHON = .venv/Scripts/python

.PHONY: run install clean

run:
	$(PYTHON) -m streamlit run ui/streamlit_app.py

install:
	$(PYTHON) -m pip install -r requirements.txt

clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
