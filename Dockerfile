FROM python:3.11-alpine

WORKDIR /app

COPY ./requirements.txt /app

RUN apk --no-cache add gcc musl-dev \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && apk del gcc musl-dev \
    && rm -rf /var/cache/apk/*

COPY . /app

EXPOSE 8084

CMD ["python", "./BatterySimulatorController.py"]
