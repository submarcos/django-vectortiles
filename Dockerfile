ARG PYTHON_VERSION=3.13

FROM ubuntu:noble AS base

ENV PYTHONBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN uv python install ${PYTHON_VERSION}

RUN mkdir -p /code/src
WORKDIR /code/src

RUN useradd -ms /bin/bash django
RUN chown -R django:django /code

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get -qq update && apt-get -qq install -y \
        gettext \
        postgresql-client \
        tzdata \
        gdal-bin \
        binutils \
        libproj-dev

EXPOSE 8000

FROM base AS build

ARG PYTHON_VERSION

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update -qq && apt-get install -y -qq \
        git \
        build-essential \
        libpq-dev

USER django

RUN uv venv -p $PYTHON_VERSION /code/venv
ENV UV_PYTHON=/code/venv/bin/python
ENV UV_LINK_MODE=copy

COPY --chown=django:django README.md ./
COPY --chown=django:django pyproject.toml ./
COPY --chown=django:django vectortiles/VERSION.md vectortiles/
RUN uv pip install .

FROM build AS dev

# Install dev requirements

RUN uv pip install .[dev] -U

CMD ["/code/venv/bin/python", "runserver", "0.0.0.0:8000"]

FROM base AS prod

ENV UV_PYTHON=/code/venv/bin/python

COPY --chown=django:django --from=build /code/venv /code/venv
COPY --chown=django:django --from=build /home/django/.local/share/uv /home/django/.local/share/uv
COPY --chown=django:django pyproject.toml pyproject.toml
COPY --chown=django:django manage.py manage.py
COPY --chown=django:django vectortiles /code/src/vectortiles
COPY --chown=django:django test_vectortiles /code/src/test_vectortiles

USER django
RUN uv pip install gunicorn psycopg djangorestframework

CMD ["/code/venv/bin/gunicorn", "-b", "0.0.0.0:8000", "test_vectortiles.wsgi:application", "--workers", "1"]