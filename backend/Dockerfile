FROM python:3.11.0-slim

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

RUN pip install poetry && poetry install --no-root

CMD ["poetry", "run", "python", "main.py"]
