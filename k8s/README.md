# Kubernetes Manifests

Production-ready Kubernetes manifests for EvalOps and KnowledgeOps.

## Deployments

### EvalOps Backend
- 3 replicas (HA)
- 256Mi memory requests, 512Mi limits
- Health checks (liveness + readiness)
- Metrics on port 9090

Deploy:
```bash
kubectl apply -f evalops-configmap.yaml
kubectl apply -f evalops-deployment.yaml
```

### KnowledgeOps Backend
- 2 replicas
- 512Mi memory requests, 1Gi limits
- PostgreSQL + pgvector backend
- Health checks (liveness + readiness)

Deploy:
```bash
kubectl apply -f knowledgeops-deployment.yaml
```

## Secrets

Before deploying, create secrets:

```bash
kubectl create secret generic evalops-secrets \
  --from-literal=database-url='postgresql://user:password@host/db' \
  --from-literal=github-token='ghp_...'

kubectl create secret generic knowledgeops-secrets \
  --from-literal=database-url='postgresql://user:password@host/db' \
  --from-literal=pgvector-user='pgvector' \
  --from-literal=pgvector-password='password'
```

## Accessing Services

```bash
# Port-forward to EvalOps
kubectl port-forward svc/evalops-backend 8000:8000

# Port-forward to KnowledgeOps
kubectl port-forward svc/knowledgeops-backend 8100:8100
```

## Monitoring

View logs:
```bash
kubectl logs -f deployment/evalops-backend
kubectl logs -f deployment/knowledgeops-backend
```

Check deployment status:
```bash
kubectl describe deployment evalops-backend
kubectl describe deployment knowledgeops-backend
```

## Scaling

Scale replicas:
```bash
kubectl scale deployment evalops-backend --replicas=5
```

## Updating

Update image:
```bash
kubectl set image deployment/evalops-backend evalops=myregistry/evalops:v2.0
```

## Cleanup

Remove all resources:
```bash
kubectl delete -f evalops-configmap.yaml
kubectl delete -f evalops-deployment.yaml
kubectl delete -f knowledgeops-deployment.yaml
```
