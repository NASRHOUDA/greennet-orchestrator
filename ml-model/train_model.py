import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import joblib

print("📊 Génération des données de trafic réseau...")
np.random.seed(42)
n_samples = 10000

# Caractéristiques
hour = np.random.randint(0, 24, n_samples)
day_of_week = np.random.randint(0, 7, n_samples)
active_connections = np.random.poisson(100, n_samples)
avg_bandwidth = np.random.exponential(50, n_samples)

# Charge CPU à prédire
cpu_load = (
    0.3 * np.sin(2 * np.pi * hour / 24) +
    0.1 * np.sin(2 * np.pi * day_of_week / 7) +
    0.4 * (active_connections / 200) +
    0.2 * (avg_bandwidth / 100) +
    np.random.normal(0, 0.05, n_samples)
)
cpu_load = np.clip(cpu_load, 0, 1)

# Créer le dataset
X = np.column_stack([hour, day_of_week, active_connections, avg_bandwidth])
y = cpu_load

# Diviser et entraîner
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
model.fit(X_train, y_train)

# Évaluer
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
print(f"✅ Modèle entraîné - MAE: {mae:.4f}")

# Sauvegarder
joblib.dump(model, 'ml-model/network_load_model.pkl')
print("✅ Modèle sauvegardé dans ml-model/network_load_model.pkl")

# Test
test_features = np.array([[14, 2, 120, 45]])  # 14h, mardi, 120 connexions, 45Mbps
prediction = model.predict(test_features)[0]
print(f"📈 Test: à 14h, charge prédite = {prediction:.2%}")
