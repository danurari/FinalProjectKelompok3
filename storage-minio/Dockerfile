# MinIO version
FROM minio/minio:latest

# Healthcheck for checking if minio can recieve image file
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:9000/minio/health/live || exit 1

# Input otomitation script
COPY init-minio.sh /usr/bin/init-minio.sh
RUN chmod +x /usr/bin/init-minio.sh

# Script initialization
CMD ["/usr/bin/init-minio.sh"]