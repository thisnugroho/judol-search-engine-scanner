FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ARG APP_UID=1008
ARG APP_GID=1009

RUN groupadd -g ${APP_GID} appgroup \
  && useradd -u ${APP_UID} -g ${APP_GID} -m appuser \
  && mkdir -p /app \
  && chown -R ${APP_UID}:${APP_GID} /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./

EXPOSE 5151

USER ${APP_UID}:${APP_GID}

CMD ["gunicorn", "--bind", "0.0.0.0:5151", "app:app"]
