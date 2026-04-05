FROM nginx:1.25-alpine

RUN apk add --no-cache curl openssl

COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80 443

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -kfsS https://localhost/health || exit 1