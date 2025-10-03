from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List
import numpy as np

from .model_utils import get_model

app = FastAPI(title="Iris Classifier API")

class IrisInput(BaseModel):
    # sepal_length, sepal_width, petal_length, petal_width
    features: List[float] = Field(..., min_items=4, max_items=4)

@app.get("/health")
def health():
    return {"status": "ok v2"}

@app.post("/predict")
def predict(inp: IrisInput):
    model = get_model()
    X = np.array([inp.features])
    proba = model.predict_proba(X)[0]
    pred = int(np.argmax(proba))
    return {"pred_class": pred, "proba": [float(p) for p in proba]}
