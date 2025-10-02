from functools import lru_cache
from pathlib import Path
import joblib

MODEL_PATH = Path(__file__).with_name("model.joblib")

@lru_cache()
def get_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found at {MODEL_PATH}. Run `python train.py` first."
        )
    return joblib.load(MODEL_PATH)
