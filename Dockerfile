# Basis-Image mit Python 3.11
FROM python:3.11

# Setze das Arbeitsverzeichnis im Container
WORKDIR /app

# Kopiere die Poetry-Konfigurationsdateien und die README.md ins Image
COPY pyproject.toml poetry.lock README.md ./

# Installiere Poetry
RUN pip install poetry

# Installiere die Abhängigkeiten ohne virtuelle Umgebung und ohne Projektinstallation
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --no-root

# Kopiere den gesamten Code ins Image
COPY models /app/models
COPY main /app/main
COPY api_functions /app/api_functions
COPY database   /app/database

# Setze den Befehl zum Starten der Anwendung
ENV PYTHONPATH=/app
CMD ["python", "main/main.py"]
