import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib

np.random.seed(42)
n = 10000

hour = np.random.randint(0, 24, n)
day = np.random.randint(0, 7, n)
connections = np.random.randint(1, 20, n)   # réaliste: 1-20
bandwidth = np.random.exponential(10, n)     # réaliste: petit réseau

cpu = (
    0.3 * np.sin(2 * np.pi * hour / 24) +
    0.5 * (connections / 20) +
    0.2 * (bandwidth / 20) +
    np.random.normal(0, 0.05, n)
)
cpu = np.clip(cpu, 0, 1)

X = np.column_stack([hour, day, connections, bandwidth])
model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
model.fit(X, cpu)

joblib.dump(model, 'ml-model/network_load_model.pkl')
print("✅ Modèle réentraîné")

for conn in [2, 5, 10, 15, 20]:
    pred = model.predict([[14, 2, conn, 5]])[0]
    print(f"Connexions: {conn:2d} → CPU prédit: {pred*100:.1f}%")
