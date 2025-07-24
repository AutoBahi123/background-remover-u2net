FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git gcc libglib2.0-0 libsm6 libxrender1 libxext6

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
