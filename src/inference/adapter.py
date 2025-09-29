import json
import time
import boto3
from typing import Dict, Any
import logging
from dataclasses import dataclass

@dataclass
class InferenceMetrics:
    provider: str
    model_id: str
    latency_ms: float
    tokens_used: int
    estimated_cost_usd: float

class InferenceAdapter:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.bedrock = boto3.client('bedrock-runtime')
        self.sagemaker = boto3.client('sagemaker-runtime')
        self.cloudwatch = boto3.client('cloudwatch')
        self.logger = logging.getLogger(__name__)
    def predict(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        provider = self.config.get('provider', 'sagemaker')
        start_time = time.time()
        if provider == 'bedrock':
            response = self._bedrock_invoke(payload)
        elif provider == 'sagemaker':
            response = self._sagemaker_invoke(payload)
        else:
            response = self._local_invoke(payload)
        latency_ms = (time.time() - start_time) * 1000
        metrics = InferenceMetrics(
            provider=provider,
            model_id=self.config.get('model_id', 'unknown'),
            latency_ms=latency_ms,
            tokens_used=response.get('token_count', 0),
            estimated_cost_usd=self._calculate_cost(response)
        )
        self._log_metrics(metrics)
        if metrics.estimated_cost_usd > self.config['cost']['per_inference_limit_usd']:
            self.logger.warning(f"Inference cost exceeded limit: {metrics.estimated_cost_usd}")
        return response
    def _bedrock_invoke(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        response = self.bedrock.invoke_model(
            modelId=self.config['bedrock']['model_id'],
            body=json.dumps({
                "prompt": payload.get('prompt', ''),
                "max_tokens": self.config['bedrock']['max_tokens'],
                "temperature": 0.7
            })
        )
        result = json.loads(response['body'].read())
        return {
            'prediction': result.get('completion', ''),
            'token_count': result.get('token_count', 0),
            'provider': 'bedrock'
        }
    def _sagemaker_invoke(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        response = self.sagemaker.invoke_endpoint(
            EndpointName=self.config['sagemaker']['endpoint_name'],
            ContentType='application/json',
            Body=json.dumps(payload)
        )
        result = json.loads(response['Body'].read())
        return {
            'prediction': result,
            'provider': 'sagemaker'
        }
    def _local_invoke(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'prediction': 'mock_prediction',
            'provider': 'local'
        }
    def _calculate_cost(self, response: Dict[str, Any]) -> float:
        if response['provider'] == 'bedrock':
            tokens = response.get('token_count', 0)
            return tokens * 0.00002
        elif response['provider'] == 'sagemaker':
            return 0.001
        return 0.0
    def _log_metrics(self, metrics: InferenceMetrics):
        self.cloudwatch.put_metric_data(
            Namespace='ML/Inference',
            MetricData=[
                {
                    'MetricName': 'Latency',
                    'Value': metrics.latency_ms,
                    'Unit': 'Milliseconds',
                    'Dimensions': [
                        {'Name': 'Provider', 'Value': metrics.provider},
                        {'Name': 'ModelId', 'Value': metrics.model_id}
                    ]
                },
                {
                    'MetricName': 'Cost',
                    'Value': metrics.estimated_cost_usd,
                    'Unit': 'None',
                    'Dimensions': [
                        {'Name': 'Provider', 'Value': metrics.provider}
                    ]
                }
            ]
        )
