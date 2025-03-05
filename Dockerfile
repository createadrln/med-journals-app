FROM python:3.10-slim

WORKDIR /app

COPY scripts/ /app/scripts/
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y cron

COPY crontab /etc/cron.d/data_collector_cron
RUN chmod 0644 /etc/cron.d/data_collector_cron && crontab /etc/cron.d/data_collector_cron

RUN mkdir -p /app/logs
RUN mkdir -p /app/raw_data

CMD ["cron", "-f"]
