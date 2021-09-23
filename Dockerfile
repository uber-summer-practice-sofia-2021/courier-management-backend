FROM python:3.9.7

RUN apt-get update \
 && apt-get install -y vim curl

WORKDIR /app

COPY requirements.txt ./
COPY fixtures/ ./fixtures/
COPY src/ ./src/

RUN pip install -r requirements.txt

EXPOSE 5000

ENV FLASK_ENV=development \
    FLASK_APP=src/app

CMD ["flask", "run", "--host=0.0.0.0"]