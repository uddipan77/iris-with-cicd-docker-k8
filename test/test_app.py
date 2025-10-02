import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from pathlib import Path
import subprocess
from fastapi.testclient import TestClient

def ensure_trained():
    model_path = Path("app") / "model.joblib"
    if not model_path.exists():
        subprocess.check_call(["python", "train.py"])

def test_predict_endpoint():
    ensure_trained()
    from app.main import app  # import after training ensures model exists
    client = TestClient(app)
    payload = {"features": [5.1, 3.5, 1.4, 0.2]}
    r = client.post("/predict", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "pred_class" in data and "proba" in data
    assert len(data["proba"]) == 3
