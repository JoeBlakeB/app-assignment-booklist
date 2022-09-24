FROM python:latest

LABEL maintainer="Joe Baker <JoeBlakeB>" \
      version="1.1.1" \
      description="eBook Library Server"
STOPSIGNAL SIGINT
ENV PUID=1000 \
    PGID=1000

WORKDIR /app
COPY . .

RUN groupadd -g $PGID -o booklist
RUN useradd -m -u $PUID -g $PGID -o -s /bin/bash booklist
RUN mkdir /data && chown -R booklist:booklist /data
USER booklist
VOLUME /data

RUN pip install -r requirements.txt --no-warn-script-location

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://127.0.0.1:8080/ || exit 1

ENTRYPOINT ["/usr/local/bin/python3", "server.py", "--port", "8080", "--data-dir", "/data"]