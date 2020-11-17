FROM alpine:latest

ENV CONFIG_FILE=/dyndns.conf
ENV CHECK_INTERVAL=1800
ENV PUID=41025

COPY dyndns.py docker/docker-entrypoint.sh /

RUN apk add --no-cache python3 py3-requests && \
    chmod +x docker-entrypoint.sh

USER $PUID:$PUID

ENTRYPOINT ["/docker-entrypoint.sh"]
