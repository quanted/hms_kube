#FROM mongo:latest
#COPY start_mongo.sh /usr/local/bin
#RUN chmod +x /usr/local/bin/start_mongo.sh
#
#ENTRYPOINT ["/usr/local/bin/start_mongo.sh"]
#
#EXPOSE 27017
#CMD ["mongod"]

FROM mongo:5.0.6-focal
USER root

RUN apt autoremove -y
RUN apt update -y
RUN apt upgrade -y

RUN chown -R mongodb:mongodb /var/log /data/db
USER mongodb