#!/bin/sh

# Running MinIO server in background (& mean background)
minio server /data --console-address ":9001" &

# Wait 5 second for the server to finish loading
sleep 5

# Read credential from docker secret 
USER=$(cat /run/secrets/minio_root_user 2>/dev/null || echo "minioadmin")
PASS=$(cat /run/secrets/minio_root_password 2>/dev/null || echo "minioadmin")

# Connect to MinIO using MinIO Clion (mc)
mc alias set myminio http://localhost:9000 $USER $PASS

# Create bucket
mc mb myminio/buku-images-bucket || true

# Set bucket permission to 'download'
mc anonymous set download myminio/buku-images-bucket || true

# Hold so the container doesn't shutdown 
wait