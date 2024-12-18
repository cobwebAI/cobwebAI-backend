FROM python:3.12

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN apt-get update -qq && apt-get install ffmpeg -y
RUN pip install poetry

ADD cobwebAI-llmlib ./cobwebAI-llmlib

RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

COPY . .

EXPOSE 8000

CMD ["python", "-m", "cobwebai"]
