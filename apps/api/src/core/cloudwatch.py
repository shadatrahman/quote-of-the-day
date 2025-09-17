"""AWS CloudWatch logging and metrics integration."""

import json
import logging
from typing import Any, Dict, Optional
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import asyncio
from datetime import datetime, timezone

from src.core.config import settings

logger = logging.getLogger(__name__)


class CloudWatchHandler(logging.Handler):
    """Custom logging handler that sends logs to AWS CloudWatch."""

    def __init__(
        self,
        log_group: str,
        log_stream: str,
        region: str = "us-east-1",
        boto3_session: Optional[boto3.Session] = None
    ):
        """Initialize CloudWatch handler."""
        super().__init__()
        self.log_group = log_group
        self.log_stream = log_stream
        self.region = region

        try:
            if boto3_session:
                self.client = boto3_session.client('logs', region_name=region)
            else:
                self.client = boto3.client('logs', region_name=region)

            # Create log group if it doesn't exist
            self._ensure_log_group_exists()

            # Create log stream if it doesn't exist
            self._ensure_log_stream_exists()

            self.sequence_token = None
            self._get_sequence_token()

        except (ClientError, NoCredentialsError) as e:
            logger.warning(f"Failed to initialize CloudWatch handler: {e}")
            self.client = None

    def _ensure_log_group_exists(self):
        """Create log group if it doesn't exist."""
        if not self.client:
            return

        try:
            self.client.create_log_group(logGroupName=self.log_group)
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceAlreadyExistsException':
                logger.warning(f"Failed to create log group {self.log_group}: {e}")

    def _ensure_log_stream_exists(self):
        """Create log stream if it doesn't exist."""
        if not self.client:
            return

        try:
            self.client.create_log_stream(
                logGroupName=self.log_group,
                logStreamName=self.log_stream
            )
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceAlreadyExistsException':
                logger.warning(f"Failed to create log stream {self.log_stream}: {e}")

    def _get_sequence_token(self):
        """Get the sequence token for the log stream."""
        if not self.client:
            return

        try:
            response = self.client.describe_log_streams(
                logGroupName=self.log_group,
                logStreamNamePrefix=self.log_stream
            )

            streams = response.get('logStreams', [])
            for stream in streams:
                if stream['logStreamName'] == self.log_stream:
                    self.sequence_token = stream.get('uploadSequenceToken')
                    break

        except ClientError as e:
            logger.warning(f"Failed to get sequence token: {e}")

    def emit(self, record: logging.LogRecord):
        """Send log record to CloudWatch."""
        if not self.client:
            return

        try:
            log_event = {
                'timestamp': int(record.created * 1000),  # CloudWatch expects milliseconds
                'message': self.format(record)
            }

            kwargs = {
                'logGroupName': self.log_group,
                'logStreamName': self.log_stream,
                'logEvents': [log_event]
            }

            if self.sequence_token:
                kwargs['sequenceToken'] = self.sequence_token

            response = self.client.put_log_events(**kwargs)
            self.sequence_token = response.get('nextSequenceToken')

        except ClientError as e:
            logger.warning(f"Failed to send log to CloudWatch: {e}")
        except Exception as e:
            logger.warning(f"Unexpected error sending log to CloudWatch: {e}")


class CloudWatchMetrics:
    """CloudWatch metrics client for custom application metrics."""

    def __init__(self, namespace: str = "Quote/API", region: str = "us-east-1"):
        """Initialize CloudWatch metrics client."""
        self.namespace = namespace
        self.region = region

        try:
            self.client = boto3.client('cloudwatch', region_name=region)
        except (ClientError, NoCredentialsError) as e:
            logger.warning(f"Failed to initialize CloudWatch metrics client: {e}")
            self.client = None

    def put_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "Count",
        dimensions: Optional[Dict[str, str]] = None,
        timestamp: Optional[datetime] = None
    ) -> bool:
        """Put a single metric to CloudWatch."""
        if not self.client:
            return False

        try:
            metric_data = {
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit,
            }

            if dimensions:
                metric_data['Dimensions'] = [
                    {'Name': k, 'Value': v} for k, v in dimensions.items()
                ]

            if timestamp:
                metric_data['Timestamp'] = timestamp
            else:
                metric_data['Timestamp'] = datetime.now(timezone.utc)

            self.client.put_metric_data(
                Namespace=self.namespace,
                MetricData=[metric_data]
            )

            return True

        except ClientError as e:
            logger.warning(f"Failed to put metric {metric_name}: {e}")
            return False
        except Exception as e:
            logger.warning(f"Unexpected error putting metric {metric_name}: {e}")
            return False

    def put_metrics(self, metrics: list) -> bool:
        """Put multiple metrics to CloudWatch."""
        if not self.client or not metrics:
            return False

        try:
            # CloudWatch accepts up to 20 metrics per request
            for i in range(0, len(metrics), 20):
                batch = metrics[i:i + 20]
                self.client.put_metric_data(
                    Namespace=self.namespace,
                    MetricData=batch
                )

            return True

        except ClientError as e:
            logger.warning(f"Failed to put metrics batch: {e}")
            return False
        except Exception as e:
            logger.warning(f"Unexpected error putting metrics batch: {e}")
            return False

    def increment_counter(
        self,
        metric_name: str,
        value: int = 1,
        dimensions: Optional[Dict[str, str]] = None
    ) -> bool:
        """Increment a counter metric."""
        return self.put_metric(metric_name, value, "Count", dimensions)

    def record_time(
        self,
        metric_name: str,
        duration_ms: float,
        dimensions: Optional[Dict[str, str]] = None
    ) -> bool:
        """Record a timing metric."""
        return self.put_metric(metric_name, duration_ms, "Milliseconds", dimensions)

    def record_gauge(
        self,
        metric_name: str,
        value: float,
        unit: str = "None",
        dimensions: Optional[Dict[str, str]] = None
    ) -> bool:
        """Record a gauge metric."""
        return self.put_metric(metric_name, value, unit, dimensions)


def setup_cloudwatch_logging() -> None:
    """Setup CloudWatch logging if configured."""
    if not settings.CLOUDWATCH_LOG_GROUP or settings.is_development:
        logger.info("CloudWatch logging not configured or in development mode")
        return

    try:
        # Create CloudWatch handler
        log_stream = f"api-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
        cloudwatch_handler = CloudWatchHandler(
            log_group=settings.CLOUDWATCH_LOG_GROUP,
            log_stream=log_stream,
            region=settings.AWS_REGION
        )

        # Set formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        cloudwatch_handler.setFormatter(formatter)

        # Add handler to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(cloudwatch_handler)

        logger.info(
            "CloudWatch logging configured",
            log_group=settings.CLOUDWATCH_LOG_GROUP,
            log_stream=log_stream
        )

    except Exception as e:
        logger.warning(f"Failed to setup CloudWatch logging: {e}")


# Global CloudWatch metrics instance
cloudwatch_metrics = CloudWatchMetrics(
    namespace=f"Quote/{settings.ENVIRONMENT.title()}",
    region=settings.AWS_REGION
)


def record_api_request(
    method: str,
    endpoint: str,
    status_code: int,
    duration_ms: float
) -> None:
    """Record API request metrics."""
    dimensions = {
        'Environment': settings.ENVIRONMENT,
        'Method': method,
        'Endpoint': endpoint,
        'StatusCode': str(status_code)
    }

    # Record request count
    cloudwatch_metrics.increment_counter('APIRequests', 1, dimensions)

    # Record response time
    cloudwatch_metrics.record_time('APIResponseTime', duration_ms, dimensions)

    # Record error rate
    if status_code >= 400:
        cloudwatch_metrics.increment_counter('APIErrors', 1, dimensions)


def record_database_operation(operation: str, duration_ms: float, success: bool = True) -> None:
    """Record database operation metrics."""
    dimensions = {
        'Environment': settings.ENVIRONMENT,
        'Operation': operation,
        'Success': str(success)
    }

    cloudwatch_metrics.increment_counter('DatabaseOperations', 1, dimensions)
    cloudwatch_metrics.record_time('DatabaseOperationTime', duration_ms, dimensions)


def record_cache_operation(operation: str, hit: bool = False) -> None:
    """Record cache operation metrics."""
    dimensions = {
        'Environment': settings.ENVIRONMENT,
        'Operation': operation,
        'Result': 'Hit' if hit else 'Miss'
    }

    cloudwatch_metrics.increment_counter('CacheOperations', 1, dimensions)