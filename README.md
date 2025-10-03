# Iris ML API - Kubernetes Deployment with CI/CD

A complete ML deployment pipeline serving a scikit-learn Iris classifier via FastAPI, containerized with Docker, orchestrated by Kubernetes, and automated with GitHub Actions CI/CD.

## 📋 Overview

This project demonstrates end-to-end ML model deployment:
- **Train** a scikit-learn logistic regression model on the Iris dataset
- **Serve** predictions via a FastAPI REST API
- **Containerize** the application with Docker
- **Deploy** to Kubernetes (local Docker Desktop cluster)
- **Automate** build, test, and deployment with GitHub Actions

## 🏗️ Architecture

```
[You edit code] 
      │
      ├── git push ──────────────────────────────────────────────────────────┐
      │                                                                      │
      ▼                                                                      │
[GitHub Repo]                                                                │
      │                                                                      │
      ├─ CI job (Ubuntu):                                                    │
      │    • pip install                                                     │
      │    • train model                                                     │
      │    • pytest                                                          │
      │    • build Docker image                                              │
      │    • push image → GHCR (ghcr.io/OWNER/REPO:<sha>, :latest)           │
      │                                                                      │
      └─ triggers                                                            │
         CD job (Self-hosted Windows):                                       │
           • kubectl apply -f k8s/                                           │
           • kubectl set image deployment/iris-api api=ghcr.io/...:<sha>     │
           • kubectl rollout status                                          │
                                                                             │
Result: Kubernetes runs your new image (2 pods)                              │
                                                                             │
User (you) ──HTTP─> NodePort Service ──> Pods ──> FastAPI ──> model.predict()
```

## 🚀 Key Components

### 1. Model & API

- **`train.py`** - Trains a scikit-learn logistic regression on the Iris dataset and saves `app/model.joblib`
- **`app/main.py`** - FastAPI application with endpoints:
  - `GET /health` - Health check
  - `POST /predict` - Prediction endpoint
  - `GET /docs` - Swagger UI
- **`tests/test_app.py`** - Integration tests for the API

### 2. Container

- **`Dockerfile`** - Multi-stage build that:
  - Installs dependencies
  - Runs `train.py` to bake the model into the image
  - Launches Uvicorn server

### 3. Kubernetes

- **`k8s/deployment.yaml`** - Defines:
  - Deployment with 2 replicas
  - ClusterIP Service for internal cluster communication
  
- **`k8s/service.nodeport.yaml`** - NodePort Service for external local access

### 4. CI/CD Pipeline

GitHub Actions workflow with two jobs:

**CI Job (Ubuntu runner):**
- Install Python dependencies
- Train the model
- Run pytest
- Build Docker image
- Push to GitHub Container Registry (GHCR)

**CD Job (Self-hosted Windows runner):**
- Apply Kubernetes manifests
- Update deployment with new image
- Wait for rollout completion

## 🔑 Why Self-Hosted Runner?

**Cloud runners cannot reach your local Kubernetes cluster.**

The self-hosted runner:
- Runs on your local machine
- Has access to your `kubeconfig`
- Can execute `kubectl` commands against Docker Desktop's Kubernetes cluster
- Enables automated deployments to your local environment

## 🌐 Accessing the API

### Option 1: NodePort (Recommended for Local)

```bash
# Find the NodePort
kubectl get svc iris-api-nodeport

# Access the API
curl http://127.0.0.1:<nodePort>/health
curl -X POST http://127.0.0.1:<nodePort>/predict \
  -H "Content-Type: application/json" \
  -d '{"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}'

# Swagger UI
open http://127.0.0.1:<nodePort>/docs
```

### Option 2: Port Forward

```bash
kubectl port-forward svc/iris-api-svc 8080:80

# Access at
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/docs
```

## 🛠️ Setup Instructions

### Prerequisites

- Docker Desktop with Kubernetes enabled
- Python 3.9+
- kubectl configured for docker-desktop context
- GitHub account with Actions enabled

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Train the model
python train.py

# Run the API locally
uvicorn app.main:app --reload

# Run tests
pytest tests/
```

### Docker Build & Run

```bash
# Build image
docker build -t iris-api:latest .

# Run container
docker run -p 8080:80 iris-api:latest

# Test
curl http://localhost:8080/health
```

### Kubernetes Deployment

```bash
# Apply manifests
kubectl apply -f k8s/

# Check deployment
kubectl get deployments
kubectl get pods
kubectl get services

# View logs
kubectl logs -l app=iris-api

# Scale deployment
kubectl scale deployment iris-api --replicas=3
```

### GitHub Actions Setup

1. **Enable Kubernetes in Docker Desktop:**
   - Settings → Kubernetes → Enable Kubernetes

2. **Set up self-hosted runner:**
   - Go to repo Settings → Actions → Runners → New self-hosted runner
   - Follow instructions to install on your Windows machine
   - Runner will have access to your local kubectl

3. **Configure GitHub Secrets:**
   - `GHCR_TOKEN` - GitHub Personal Access Token with `write:packages` scope

4. **Push to trigger workflow:**
   ```bash
   git add .
   git commit -m "Deploy to Kubernetes"
   git push origin main
   ```

## 📦 Project Structure

```
.
├── app/
│   ├── main.py          # FastAPI application
│   └── model.joblib     # Trained model (generated)
├── k8s/
│   ├── deployment.yaml  # Kubernetes Deployment + ClusterIP Service
│   └── service.nodeport.yaml  # NodePort Service
├── tests/
│   └── test_app.py      # API tests
├── .github/
│   └── workflows/
│       └── ci-cd.yaml   # GitHub Actions workflow
├── train.py             # Model training script
├── Dockerfile           # Container definition
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🧪 API Examples

### Health Check

```bash
curl http://127.0.0.1:<nodePort>/health
```

**Response:**
```json
{
  "status": "healthy"
}
```

### Predict

```bash
curl -X POST http://127.0.0.1:<nodePort>/predict \
  -H "Content-Type: application/json" \
  -d '{
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2
  }'
```

**Response:**
```json
{
  "prediction": "setosa",
  "confidence": 0.95
}
```

## 🔄 Workflow

1. **Develop:** Make changes to code locally
2. **Test:** Run tests locally with `pytest`
3. **Commit:** Push changes to GitHub
4. **CI:** GitHub Actions builds, tests, and pushes Docker image
5. **CD:** Self-hosted runner deploys to local Kubernetes cluster
6. **Access:** Use NodePort or port-forward to test the deployed API

## 📊 Monitoring & Debugging

```bash
# View pod logs
kubectl logs -f deployment/iris-api

# Describe pod for events
kubectl describe pod <pod-name>

# Get all resources
kubectl get all

# Check rollout status
kubectl rollout status deployment/iris-api

# Rollback if needed
kubectl rollout undo deployment/iris-api
```

## 🎯 Next Steps

- **Add monitoring:** Prometheus + Grafana for metrics
- **Implement logging:** Centralized logging with ELK stack
- **Add ingress:** Use Ingress controller for better routing
- **Model versioning:** Track model versions with MLflow
- **A/B testing:** Deploy multiple model versions
- **Auto-scaling:** Configure HorizontalPodAutoscaler (HPA)
- **Production deployment:** Migrate to cloud Kubernetes (EKS, GKE, AKS)

## 📝 Notes

- The model is baked into the Docker image during build time
- For production, consider storing models in external storage (S3, GCS)
- Self-hosted runners should be secured and not exposed to public repos
- Always use specific image tags in production (not `:latest`)

## 📄 License

MIT

---

**Built with ❤️ using FastAPI, scikit-learn, Docker, Kubernetes, and GitHub Actions**