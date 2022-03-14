FROM mongo:latest
RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get remove golang-go
RUN chown -R mongodb:mongodb /var/log /data/db
USER mongodb
