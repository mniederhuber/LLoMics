FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

#COPY requirements.txt /app/requirements.txt

RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install -e . 

EXPOSE 8080

#CMD ["python", "sragent/gui.py"]
