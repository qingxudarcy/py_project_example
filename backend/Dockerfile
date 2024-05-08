FROM python:3.11.0-slim

ARG PIP_VERSION="24.0"
ARG POETRY_VERSION="1.8.1"

# Install basic and additional apt dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Add User
ARG WEB_USER_GID="900"
ARG WEB_USER_UID="900"
ARG WEB_USER_HOME=/home/web
ARG WEB_USER_HOME_DIR=/home/web

RUN groupadd -g "${WEB_USER_GID}"  web && \
	adduser --system  --uid "${WEB_USER_UID}" --home "${WEB_USER_HOME_DIR}" --gid "${WEB_USER_GID}" web && \
	mkdir -p ${WEB_USER_HOME} && chown -R "web:web" "${WEB_USER_HOME_DIR}" ${WEB_USER_HOME}

WORKDIR /app

RUN chown web:web /app

USER ${WEB_USER_UID}

COPY --chown=web:web ./web_app /app

RUN poetry install --no-root --only main

CMD ["poetry", "run", "python", "main.py"]
