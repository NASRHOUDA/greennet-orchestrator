FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir kubernetes requests numpy scikit-learn==1.3.0 joblib
COPY operators/energy-scaler/energy_scaler_k8s.py .
COPY ml-model/network_load_model.pkl .
CMD ["python", "-u", "energy_scaler_k8s.py"]
