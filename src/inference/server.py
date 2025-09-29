from fastapi import FastAPI, Request
import uvicorn
import yaml
import time
from adapter import InferenceAdapter
app = FastAPI()

with open("configs/dev.yaml") as f:
    config = yaml.safe_load(f)
adapter = InferenceAdapter(config)

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/predict")
def predict(request: Request):
    payload = request.json()
    result = adapter.predict(payload)
    return {
        "prediction": result["prediction"],
        "model_version": config["model"]["version"],
        "timestamp": time.time()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
