FROM mongo:latest
COPY start_mongo.sh /usr/local/bin
RUN chmod +x /usr/local/bin/start_mongo.sh

ENTRYPOINT ["/usr/local/bin/start_mongo.sh"]

EXPOSE 27017
CMD ["mongod"]