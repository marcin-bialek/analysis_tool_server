FROM python:3.11.2-alpine3.17

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.4.1

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /qdamono_server
COPY poetry.lock pyproject.toml .env /qdamono_server/

RUN poetry config virtualenvs.create false
RUN poetry install --without dev --no-interaction --no-ansi

COPY . /qdamono_server
