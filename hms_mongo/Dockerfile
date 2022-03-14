FROM mongo:latest
RUN apt-get upgrade
RUN apt-get update
RUN chown -R mongodb:mongodb /var/log /data/db
USER mongodb
