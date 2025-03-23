FROM python:3.10.12

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Лучше так не делать...
COPY . .

RUN mkdir -p /app/data
COPY graph_data.json /app/data/

EXPOSE 5000

CMD ["python", "run.py"]