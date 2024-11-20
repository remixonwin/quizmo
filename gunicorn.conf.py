import multiprocessing

# Gunicorn configuration file
bind = "0.0.0.0:8000"

# Worker configuration
workers = 4  # Fixed number of workers for predictable resource usage
worker_class = "sync"
timeout = 30

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Server mechanics
daemon = False
