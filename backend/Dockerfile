FROM python:3.11-slim

WORKDIR /app

# Копируем файлы (poetry.lock может и не быть)
COPY pyproject.toml README.md ./
COPY poetry.lock* ./

# Установка Poetry и зависимостей
RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && if [ -f poetry.lock ]; then \
        poetry install --no-interaction --no-ansi --no-root; \
    else \
        poetry install --no-interaction --no-ansi --no-root; \
    fi \
    && pip install --no-cache-dir python-multipart

COPY . .

ENV PYTHONPATH=/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]