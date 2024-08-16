FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y curl uvicorn

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"

COPY pyproject.toml poetry.lock* /app/

RUN poetry install --no-root

COPY . /app

CMD ["poetry", "run", "streamlit", "run", "src/app.py"]