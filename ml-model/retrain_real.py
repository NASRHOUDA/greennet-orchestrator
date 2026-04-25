#!/usr/bin/env python3
import requests
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib
from datetime import datetime, timedelta

PROMETHEUS = "http://localhost:9090"

def query_range(metric, start, end, step="15s"):
    resp = requests.get(f"{PROMETHEUS}/api/v1/query_range", params={
        "query": metric,
        "start": start.timestamp(),
        "end": end.timestamp(),
        "step": step
    }, timeout=10)
    data = resp.json()
    if data["status"] == "success" and data["data"]["result"]:
        return [(float(ts), float(val)) for ts, val in data["data"]["result"][0]["values"]]
    return []

# Prendre TOUT l'historique disponible (6h)
end = datetime.now()
start = end - timedelta(hours=6)

print("📡 Récupération des données Prometheus...")
connections_data = query_range("nginx_connections_active", start, end)
cpu_data = query_range("rate(process_cpu_seconds_total[1m])", start, end)

print(f"   Connexions: {len(connections_data)} points")
print(f"   CPU: {len(cpu_data)} points")

if len(connections_data) < 50:
    print(f"⚠️ Seulement {len(connections_data)} points — attendre plus de données")
    exit(1)

conn_dict = dict(connections_data)
cpu_dict = dict(cpu_data)
common_ts = set(conn_dict.keys()) & set(cpu_dict.keys())

X, y = [], []
for ts in sorted(common_ts):
    dt = datetime.fromtimestamp(ts)
    conn = conn_dict[ts]
    cpu = min(cpu_dict[ts] * 100, 1.0)
    X.append([dt.hour, dt.weekday(), conn, 5.0])
    y.append(cpu)

X = np.array(X)
y = np.array(y)
print(f"\n📊 Dataset: {len(X)} échantillons")
print(f"   Connexions: min={X[:,2].min():.0f}, max={X[:,2].max():.0f}, mean={X[:,2].mean():.1f}")
print(f"   CPU: min={y.min()*100:.1f}%, max={y.max()*100:.1f}%, mean={y.mean()*100:.1f}%")

model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
model.fit(X, y)
joblib.dump(model, "ml-model/network_load_model.pkl")
print("\n✅ Modèle réentraîné")

print("\n📈 Prédictions:")
for conn in range(1, 17):
    pred = model.predict([[datetime.now().hour, datetime.now().weekday(), conn, 5.0]])[0]
    print(f"   Connexions: {conn:2d} → CPU prédit: {pred*100:.1f}%")
