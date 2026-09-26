FROM python:3.12-slim

WORKDIR /app

COPY . .

# Install nginx for serving static files
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

# Copy nginx config for serving static files and proxying to Flask
RUN echo 'server { listen 80; root /app; index web3_cookie_demo.html; location / { try_files $uri $uri/ =404; } location /socket.io { proxy_pass http://localhost:5000; proxy_http_version 1.1; proxy_set_header Upgrade $http_upgrade; proxy_set_header Connection "upgrade"; proxy_set_header Connection "upgrade"; proxy_buffering off; } location /api { proxy_pass http://localhost:5000; } }' > /etc/nginx/sites-available/default

RUN python3 -m venv /app/venv && \
    . /app/venv/bin/activate && \
    pip install --no-cache-dir \
    python-osc \
    web3 \
    prometheus-client \
    requests \
    websocket-client \
    flask \
    flask-socketio \
    python-socketio \
    requests-html \
    beautifulsoup4 \
    lxml

# Expose ports for nginx (80), Flask (5000), OSC (9000), Prometheus (8000)
EXPOSE 80 5000 9000 8000

CMD ["sh", "-c", "service nginx start && . /app/venv/bin/activate && python ableton_vdmx_web3_bridge.py"]
