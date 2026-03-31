# Database version
FROM postgres:15-alpine

# Healthcheck For checking if docker swarm knowing the DB is ready or not
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD pg_isready -U postgres || exit 1

# Set timezone to Indonesian times
ENV TZ=Asia/Jakarta
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone