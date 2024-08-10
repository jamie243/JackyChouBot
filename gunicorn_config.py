# gunicorn_config.py

bind = "0.0.0.0:8000"  # The address and port Gunicorn should bind to
workers = 3           # The number of worker processes for handling requests
threads = 2           # The number of threads for handling requests in each worker
timeout = 120         # Workers silent for more than this many seconds are killed and restarted
loglevel = "info"     # The granularity of `gunicorn` log output (debug, info, warning, error, critical)

# Optional settings
accesslog = "-"       # The access log file to write to, "-" means stdout
errorlog = "-"        # The error log file to write to, "-" means stderr
