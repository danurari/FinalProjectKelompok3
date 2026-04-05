FROM prom/prometheus:latest

COPY prometheus.yml /etc/prometheus/prometheus.yml

EXPOSE 9090

CMD [ \
    "--config.file=/etc/prometheus/prometheus.yml", \
    "--storage.tsdb.path=/prometheus", \
    "--storage.tsdb.retention.time=15d", \
    "--web.enable-lifecycle", \
    "--web.external-url=/prometheus/", \
    "--web.route-prefix=/" \
]



  