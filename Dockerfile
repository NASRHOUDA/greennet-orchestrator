FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir --upgrade numpy scikit-learn
RUN pip install --no-cache-dir kubernetes requests joblib
COPY operators/energy-scaler/energy_scaler.py .
COPY ml-model/network_load_model.pkl .
CMD ["python", "-u", "energy_scaler.py"]
