FROM grafana/grafana:latest

ENV GF_SERVER_ROOT_URL http://layananbuku.netdev/grafana/
ENV GF_SERVER_SERVE_FROM_SUB_PATH true
ENV GF_AUTH_ANONYMOUS_ENABLED=false
ENV GF_DEFAULT_TIMEZONE=Asia/Jakarta

COPY provisioning/ /etc/grafana/provisioning/
COPY --chmod=755 entrypoint.sh /entrypoint.sh

EXPOSE 3000

ENTRYPOINT ["/entrypoint.sh"]
