# FROM nginx:stable
FROM nginx:stable-alpine3.17-slim

RUN rm /etc/nginx/conf.d/default.conf

ARG CONFIG=nginx.conf

COPY $CONFIG /etc/nginx/conf.d/