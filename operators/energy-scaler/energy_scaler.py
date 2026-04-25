#!/usr/bin/env python3
import time
import requests
import joblib
import numpy as np
import os
import sys
from datetime import datetime
from kubernetes import client, config

sys.stdout.reconfigure(line_buffering=True)

class EnergyScalerK8s:
    def __init__(self):
        try:
            config.load_incluster_config()
            print("✅ Config Kubernetes (in-cluster)", flush=True)
        except:
            config.load_kube_config()
            print("✅ Config Kubernetes (local)", flush=True)

        self.apps_v1 = client.AppsV1Api()
        self.threshold_high = 25
        self.threshold_low = 21
        self.min_replicas = 1
        self.max_replicas = 5
        self.last_scale_time = 0
        self.cooldown_seconds = 120
        self.prometheus_url = os.environ.get(
            'PROMETHEUS_URL',
            'http://prometheus-kube-prometheus-prometheus.monitoring:9090'
        )

        try:
            self.model = joblib.load('/app/network_load_model.pkl')
            print("✅ Modèle ML chargé", flush=True)
            self.use_ml = True
        except Exception as e:
            print(f"⚠️ Modèle non chargé: {e}", flush=True)
            self.model = None
            self.use_ml = False

    def get_connections(self):
        try:
            resp = requests.get(
                f"{self.prometheus_url}/api/v1/query",
                params={'query': 'nginx_connections_active'},
                timeout=5
            )
            if resp.status_code == 200:
                data = resp.json()
                if data['data']['result']:
                    return float(data['data']['result'][0]['value'][1])
        except Exception as e:
            print(f"⚠️ Prometheus error: {e}", flush=True)
        return 0.0

    def predict_cpu(self, connections):
        now = datetime.now()
        hour = now.hour
        day_of_week = now.weekday()
        avg_bandwidth = 50.0  # estimation fixe en Mbps

        features = np.array([[hour, day_of_week, connections, avg_bandwidth]])
        cpu_ratio = self.model.predict(features)[0]
        return float(np.clip(cpu_ratio * 100, 0, 100))

    def scale(self, namespace, deployment, cpu):
        try:
            dep = self.apps_v1.read_namespaced_deployment(deployment, namespace)
            current = dep.spec.replicas or 1
            new = current

            if cpu > self.threshold_high and current < self.max_replicas:
                new = current + 1
                print(f"🔺 Scale UP: {current} → {new} réplica(s) (CPU: {cpu:.1f}%)", flush=True)
            elif cpu < self.threshold_low and current > self.min_replicas:
                new = current - 1
                print(f"🔻 Scale DOWN: {current} → {new} réplica(s) (CPU: {cpu:.1f}%)", flush=True)
            else:
                print(f"✓ Maintien: {current} réplica(s)", flush=True)

            if new != current:
                dep.spec.replicas = new
                self.apps_v1.patch_namespaced_deployment(deployment, namespace, dep)
                self.last_scale_time = __import__('time').time()
        except Exception as e:
            print(f"⚠️ Erreur scale: {e}", flush=True)

    def run(self):
        print("=" * 50, flush=True)
        print("ENERGY SCALER - GREENNET (ML)", flush=True)
        print(f"Prometheus: {self.prometheus_url}", flush=True)
        print(f"Mode ML: {'✅ actif' if self.use_ml else '❌ fallback x5'}", flush=True)
        print("=" * 50, flush=True)

        while True:
            try:
                connections = self.get_connections()

                if connections == 0:
                    print(f"[⏭️ Skip] 0 connexions, pas de scaling", flush=True)
                    time.sleep(30)
                    continue

                if self.use_ml:
                    cpu = self.predict_cpu(connections)
                    print(f"[🧠 ML] Connexions: {connections:.1f} → CPU prédit: {cpu:.1f}%", flush=True)
                else:
                    cpu = min(connections * 5, 100)
                    print(f"[📊 Fallback] Connexions: {connections:.1f} → CPU: {cpu:.1f}%", flush=True)

                import time as _t
                now = _t.time()
                if now - self.last_scale_time < self.cooldown_seconds:
                    remaining = int(self.cooldown_seconds - (now - self.last_scale_time))
                    print(f"[⏳ Cooldown] {remaining}s restantes", flush=True)
                else:
                    self.scale('default', 'webserver', cpu)

            except Exception as e:
                print(f"❌ Erreur boucle: {e}", flush=True)

            time.sleep(30)

if __name__ == '__main__':
    EnergyScalerK8s().run()
