# Catalog Service

The Catalog Service manages products and inventory for the online store.

## Responsibilities

- Create products.
- List products.
- Read product details.
- Update product stock.
- Reserve stock for orders.

## Run Locally

```powershell
cd D:\Mtech\Sem3\Scalable\Assignment\catalog-service
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

## Run Tests

```powershell
cd D:\Mtech\Sem3\Scalable\Assignment\catalog-service
pytest
```

## Pre-commit

This repository has its own pre-commit configuration in `.pre-commit-config.yaml`.

```powershell
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/health` | Health check |
| POST | `/products` | Create product |
| GET | `/products` | List products |
| GET | `/products/{product_id}` | Get product |
| PATCH | `/products/{product_id}/stock` | Update stock |
| POST | `/products/{product_id}/reserve` | Reserve stock |

## Docker

Build the image:

```powershell
docker build -t catalog-service:1.0 .
```

Run the container:

```powershell
docker run -d --name catalog-service -p 8001:8000 catalog-service:1.0
```

## Kubernetes

This repository owns its own Kubernetes manifests in the `k8s` folder.

For Minikube:

```powershell
minikube start
minikube docker-env | Invoke-Expression
docker build -t catalog-service:1.0 .
kubectl apply -f .\k8s\namespace.yaml
kubectl apply -f .\k8s\deployment.yaml
kubectl get all -n store-app
```

Access the service:

```powershell
minikube service catalog-service -n store-app
```

## GitHub Actions

This repository has its own workflow:

```text
.github/workflows/ci.yml
```

The workflow runs pre-commit checks, runs tests, and builds the Docker image.

The current workflow does not need credentials because it does not push images or deploy to a cloud cluster. If Docker image push is added later, add these secrets in GitHub repository `Settings` -> `Secrets and variables` -> `Actions`:

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

Never hardcode passwords, tokens, or kubeconfig values in the workflow file.
