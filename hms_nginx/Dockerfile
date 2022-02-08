FROM nginx:stable

RUN rm /etc/nginx/conf.d/default.conf

ARG CONFIG=nginx.conf

COPY $CONFIG /etc/nginx/conf.d/