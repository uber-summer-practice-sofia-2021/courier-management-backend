FROM python:3.8-slim

RUN apt-get update \
 && apt-get install -y vim curl

WORKDIR /app

COPY requirements.txt ./
COPY fixtures/ ./fixtures/
COPY src/ ./src/

RUN pip install -r requirements.txt

EXPOSE 5000

ENV FLASK_ENV=development \
    FLASK_APP=src/app \
    ORDER_MANAGEMENT_HOST=localhost \
    ORDER_MANAGEMENT_PORT=5000 \
    KAFKA_BROKERS=kafka:9092 \
    KAFKA_TOPIC=trips \
    DATABASE_HOST= \
    DATABASE_PORT= \
    DATABASE_USERNAME= \
    DATABASE_PASSWD= \
    DATABASE_PATH=db/server.db \
    DATABASE_DIALECT=sqlite \
    DATABASE_DRIVER=

CMD ["flask", "run", "--host=0.0.0.0"]