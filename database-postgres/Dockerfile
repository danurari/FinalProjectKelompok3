FROM postgres:15-alpine

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD pg_isready -U $$(cat /run/secrets/postgres_user) -d $$(cat /run/secrets/postgres_db) || exit 1

ENV TZ=Asia/Jakarta
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

CMD ["postgres", "-c", "max_connections=200", "-c", "shared_buffers=128MB"]

COPY init.sql /docker-entrypoint-initdb.d