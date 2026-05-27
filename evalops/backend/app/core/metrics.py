from prometheus_client import Gauge, make_asgi_app

reliability_score = Gauge(
    "evalops_reliability_score",
    "Last computed reliability score (0-100)",
)
hallucination_rate = Gauge(
    "evalops_hallucination_rate",
    "Hallucination risk from most recent completed evaluation (0-1)",
)

metrics_app = make_asgi_app()
