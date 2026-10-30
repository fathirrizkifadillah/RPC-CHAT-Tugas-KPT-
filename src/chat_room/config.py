"""Konfigurasi default untuk Distributed Chat Room gRPC."""

DEFAULT_HOST: str = "0.0.0.0"
DEFAULT_PORT: int = 50051
DEFAULT_SERVER_ADDRESS: str = f"localhost:{DEFAULT_PORT}"

# Concurrency & Worker pool
DEFAULT_MAX_WORKERS: int = 30

# Antrean & Kapasitas Buffer
DEFAULT_CLIENT_QUEUE_MAXSIZE: int = 100
DEFAULT_STREAM_POLL_TIMEOUT: float = 0.5  # Detik untuk mendeteksi status context aktif

# Deduplikasi & Batas Cache PROSES
DEFAULT_MAX_PROSES_CACHE: int = 10000

# Client Resilience (Timeout & Retry)
DEFAULT_UNARY_TIMEOUT: float = 5.0
DEFAULT_MAX_RETRIES: int = 3
DEFAULT_BASE_RETRY_DELAY: float = 0.5
