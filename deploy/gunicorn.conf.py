# Gunicorn 配置
bind = "0.0.0.0:8050"
workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
