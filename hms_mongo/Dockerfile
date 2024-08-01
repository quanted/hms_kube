# FROM ghcr.io/quanted/mongo:7.0.9
# USER root
# #RUN chown -R mongodb:mongodb /var/log /data/db
# #USER mongodb



FROM ubuntu:24.10
ENV MONGO_VERSION=6.0.16

RUN apt-get update && apt-get install -y gnupg curl

RUN curl -fsSL https://pgp.mongodb.com/server-6.0.asc | \
	gpg -o /usr/share/keyrings/mongodb-server-6.0.gpg \
	--dearmor

RUN echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list

RUN apt-get update && \
	apt-get install -y \
		mongodb-org=${MONGO_VERSION} \
		mongodb-org-database=${MONGO_VERSION} \
		mongodb-org-server=${MONGO_VERSION} \
		mongodb-org-mongos=${MONGO_VERSION} \
		mongodb-org-tools=${MONGO_VERSION}

RUN mkdir -p /data/db

EXPOSE 27017/tcp

CMD ["/usr/bin/mongod"]
