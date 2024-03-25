# FROM nginx:stable
FROM nginx:stable-alpine3.17-slim

RUN apk update && \
	apk upgrade

RUN rm -rf /usr/share/nginx/html/* && \
	rm /etc/nginx/conf.d/default.conf

ARG CONFIG=nginx.conf

COPY $CONFIG /etc/nginx/conf.d/