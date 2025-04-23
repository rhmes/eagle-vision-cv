FROM python:3.11

WORKDIR /engine

COPY requirements.txt .
RUN apt-get update && apt-get install -y \
    libsm6 \
    libxext6 \
    libgl1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

CMD ["python", "processor.py"]

EXPOSE 5000
CMD ["uvicorn", "main:engine", "--host", "0.0.0.0", "--port", "5000", "--log-level", "warning"]
