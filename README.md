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
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

## Run Tests

```powershell
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

## Testing the API

### Health Check

**PowerShell:**

```powershell
Invoke-RestMethod http://localhost:8001/health
```

**Bash/Git Bash:**

```bash
curl http://localhost:8001/health
```

### Create a Product

**PowerShell:**

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8001/products -ContentType "application/json" -Body '{"name":"Laptop","description":"Student laptop","price":55000,"stock":10}'
```

**Bash/Git Bash:**

```bash
curl -X POST http://localhost:8001/products \
  -H "Content-Type: application/json" \
  -d '{"name":"Laptop","description":"Student laptop","price":55000,"stock":10}'
```

### List Products

**PowerShell:**

```powershell
Invoke-RestMethod http://localhost:8001/products
```

**Bash/Git Bash:**

```bash
curl http://localhost:8001/products
```

### Get Product Details

**PowerShell:**

```powershell
Invoke-RestMethod http://localhost:8001/products/1
```

**Bash/Git Bash:**

```bash
curl http://localhost:8001/products/1
```

### Update Product Stock

**PowerShell:**

```powershell
Invoke-RestMethod -Method Patch -Uri http://localhost:8001/products/1/stock -ContentType "application/json" -Body '{"quantity":5}'
```

**Bash/Git Bash:**

```bash
curl -X PATCH http://localhost:8001/products/1/stock \
  -H "Content-Type: application/json" \
  -d '{"quantity":5}'
```

### Reserve Product Stock

**PowerShell:**

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8001/products/1/reserve -ContentType "application/json" -Body '{"quantity":2}'
```

**Bash/Git Bash:**

```bash
curl -X POST http://localhost:8001/products/1/reserve \
  -H "Content-Type: application/json" \
  -d '{"quantity":2}'
```

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

### Kubernetes Dashboard

Enable and open the dashboard:

```powershell
minikube dashboard
```

In the dashboard:

- Select the namespace `store-app` then check the resources:
  - Deployments: `catalog-service`
  - Pods: running status and restart count
  - Services: NodePort service exposure
  - Logs: request handling and any service communication errors


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
