# Kubernetes Deployment Plan

1. Build and push backend image to registry.
2. Apply base manifests with Kustomize overlays.
3. Add HPA and PodDisruptionBudgets.
4. Configure Secrets for model/API credentials.
5. Deploy Prometheus and Grafana in monitoring namespace.
6. Add alert rules for hallucination and latency spikes.
7. Promote from dev to staging to prod with progressive rollout.
