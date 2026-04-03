FROM minio/minio:latest

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:9000/minio/health/live || exit 1

COPY init-minio.sh /usr/bin/init-minio.sh
RUN chmod +x /usr/bin/init-minio.sh

ENTRYPOINT ["/usr/bin/init-minio.sh"]