FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt \
    && groupadd --system golfiq \
    && useradd --system --gid golfiq --create-home golfiq

COPY --chown=golfiq:golfiq app ./app
COPY --chown=golfiq:golfiq alembic ./alembic
COPY --chown=golfiq:golfiq alembic.ini ./alembic.ini
COPY --chown=golfiq:golfiq scripts/start.sh ./scripts/start.sh

# Normalize Windows line endings and make startup independent of host file modes.
RUN sed -i 's/\r$//' ./scripts/start.sh \
    && chmod 755 ./scripts/start.sh

USER golfiq

EXPOSE 8000

ENTRYPOINT ["./scripts/start.sh"]
