FROM python:3.12-slim as base
ENV  POETRY_VERSION=1.8.4 \
  PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_HOME="/opt/poetry" \
  POETRY_VIRTUALENVS_IN_PROJECT=true \
  POETRY_NO_INTERACTION=1 \
  PYSETUP_PATH="/opt/pysetup" \
  VENV_PATH="/opt/pysetup/.venv"
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"
 
 
FROM base as builder
RUN --mount=type=cache,target=/root/.cache \
  pip install "poetry==$POETRY_VERSION"
WORKDIR $PYSETUP_PATH
COPY ./poetry.lock ./pyproject.toml ./
RUN --mount=type=cache,target=$POETRY_HOME/pypoetry/cache \
  poetry install --no-dev
 
 
FROM base as production
ENV FASTAPI_ENV=production
COPY --from=builder $VENV_PATH $VENV_PATH
COPY ./cobwebai /cobwebai
WORKDIR /cobwebai
EXPOSE 8000
CMD ["python", "__main__.py"]