FROM mongo:latest
#COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chown -R mongodb:mongodb /var/log /data/db
USER mongodb
#ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]