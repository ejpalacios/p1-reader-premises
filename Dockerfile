FROM python:3.9-slim AS base

WORKDIR /app

COPY requirements/prod.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY p1reader p1reader

FROM base AS p1-reader
CMD [ "python", "-m", "p1reader"]
