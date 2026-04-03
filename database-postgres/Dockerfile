# Database version
FROM postgres:15-alpine

# Healthcheck For checking if docker swarm knowing the DB is ready or not
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD pg_isready -U $$(cat /run/secrets/postgres_user) -d $$(cat /run/secrets/postgres_db) || exit 1

# Set timezone to Indonesian times
ENV TZ=Asia/Jakarta
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Performance Tuning for resource optimization
CMD ["postgres", "-c", "max_connections=200", "-c", "shared_buffers=128MB"]

# SQL setup script Initialization
COPY init.sql /docker-entrypoint-initdb.d