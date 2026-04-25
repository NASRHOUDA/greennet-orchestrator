FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY energy_scaler.py .
COPY ../../ml-model/network_load_model.pkl .

CMD ["python", "energy_scaler.py"]
