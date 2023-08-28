# FROM ghcr.io/quanted/mongo:5.0.6
# #USER root
# #RUN chown -R mongodb:mongodb /var/log /data/db
# #USER mongodb



FROM ubuntu:22.10

RUN apt-get update && apt-get install -y gnupg curl

RUN curl -fsSL https://pgp.mongodb.com/server-6.0.asc | \
	gpg -o /usr/share/keyrings/mongodb-server-6.0.gpg \
	--dearmor

RUN echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list

RUN apt-get update && \
	apt-get install -y \
		mongodb-org=6.0.8 \
		mongodb-org-database=6.0.8 \
		mongodb-org-server=6.0.8 \
		mongodb-org-mongos=6.0.8 \
		mongodb-org-tools=6.0.8

RUN mkdir -p /data/db

EXPOSE 27017/tcp

CMD ["/usr/bin/mongod"]