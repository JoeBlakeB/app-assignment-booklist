FROM python:latest

LABEL maintainer="Joe Baker <JoeBlakeB>"
LABEL version="1.1.0"
LABEL description="eBook Library Server"
STOPSIGNAL SIGINT

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://127.0.0.1:8080/ || exit 1

ENTRYPOINT ["/usr/local/bin/python3", "server.py", "--port", "8080", "--data-dir", "/data"]