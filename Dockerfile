FROM python:3.8-slim

RUN apt-get update \
 && apt-get install -y vim curl python3-dev default-libmysqlclient-dev gcc

WORKDIR /app

COPY requirements.txt ./
COPY fixtures/ ./fixtures/
COPY src/ ./src/

RUN pip install -r requirements.txt

EXPOSE 5000

ENV FLASK_ENV=development \
    FLASK_APP=src/app \
    ORDER_MANAGEMENT_HOST=order-Publi-DVY752SUI77Y-1625392201.eu-west-1.elb.amazonaws.com \
    ORDER_MANAGEMENT_PORT=80 \
    KAFKA_BROKERS=kafka:9092 \
    KAFKA_TOPIC=trips \
    DATABASE_HOST=database \
    DATABASE_PORT=3306 \
    DATABASE_USERNAME=root \
    DATABASE_PASSWD=secret \
    DATABASE_PATH=courier_management \
    DATABASE_DIALECT=mysql \
    DATABASE_DRIVER=

CMD ["flask", "run", "--host=0.0.0.0"]