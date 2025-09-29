from fastapi import FastAPI, UploadFile, File
import gradio as gr
import pandas as pd
from src.inference.adapter import InferenceAdapter
import yaml

app = FastAPI()

with open("configs/dev.yaml") as f:
    config = yaml.safe_load(f)
adapter = InferenceAdapter(config)

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/predict")
def predict(data: dict):
    result = adapter.predict(data)
    return result

def gradio_ui():
    def predict_gradio(input_data):
        result = adapter.predict({"input": input_data})
        return result.get("prediction", "No prediction")
    demo = gr.Interface(
        fn=predict_gradio,
        inputs=gr.Textbox(label="Input Data"),
        outputs=gr.Textbox(label="Prediction"),
        title="ML Pipeline Inference UI"
    )
    demo.launch()

if __name__ == "__main__":
    import uvicorn
    import threading
    threading.Thread(target=gradio_ui).start()
    uvicorn.run(app, host="0.0.0.0", port=8080)