#!/bin/sh

if [ -f /run/secrets/grafana_admin_user ]; then
    export GF_SECURITY_ADMIN_USER=$(cat /run/secrets/grafana_admin_user)
    echo "✅ grafana_admin_user berhasil dibaca dari secret"
else
    echo "⚠️  Secret grafana_admin_user tidak ditemukan, pakai default"
    export GF_SECURITY_ADMIN_USER=admin

fi

if [ -f /run/secrets/grafana_admin_password ]; then
    export GF_SECURITY_ADMIN_PASSWORD=$(cat /run/secrets/grafana_admin_password)
    echo "✅ grafana_admin_password berhasil dibaca dari secret"
else
    echo "⚠️  Secret grafana_admin_password tidak ditemukan, pakai default"
    export GF_SECURITY_ADMIN_PASSWORD=admin123
fi

exec /run.sh

