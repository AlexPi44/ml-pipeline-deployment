import pytest
import requests
import json
import time
import yaml
import os
class TestCanaryDeployment:
    @classmethod
    def setup_class(cls):
        env = os.getenv("ENVIRONMENT", "staging")
        with open(f"configs/{env}.yaml") as f:
            cls.config = yaml.safe_load(f)
        cls.endpoint_url = f"https://{env}.api.example.com/predict"
    def test_health_check(self):
        response = requests.get(f"{self.endpoint_url}/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    def test_inference_latency(self):
        payload = {"input": "test_data"}
        start = time.time()
        response = requests.post(self.endpoint_url, json=payload)
        latency_ms = (time.time() - start) * 1000
        assert response.status_code == 200
        assert latency_ms < self.config["monitoring"]["latency_threshold_ms"]
    def test_response_format(self):
        payload = {"input": "test_data"}
        response = requests.post(self.endpoint_url, json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert "model_version" in data
        assert "timestamp" in data
    def test_error_handling(self):
        payload = {"invalid": "data"}
        response = requests.post(self.endpoint_url, json=payload)
        assert response.status_code == 400
        assert "error" in response.json()
