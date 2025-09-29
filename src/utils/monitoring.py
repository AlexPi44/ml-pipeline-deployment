import prometheus_client
from prometheus_client import Counter, Histogram

inference_count = Counter('inference_count', 'Total inferences')
latency_histogram = Histogram('inference_latency_ms', 'Inference latency (ms)')

def log_inference(latency):
    inference_count.inc()
    latency_histogram.observe(latency)
