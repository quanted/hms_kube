# FROM nginx:stable
FROM nginx:stable-alpine3.17-slim

ARG APP_USER=nginx

RUN apk update && \
	apk upgrade --available

RUN rm -rf /usr/share/nginx/html/* && \
	rm /etc/nginx/conf.d/default.conf

ARG CONFIG=nginx.conf

COPY $CONFIG /etc/nginx/conf.d/

RUN mkdir /src
RUN chown -R $APP_USER:$APP_USER /src && chmod -R 755 /src && \
        chown -R $APP_USER:$APP_USER /etc/nginx/conf.d && \
        chown -R $APP_USER:$APP_USER /var/cache/nginx
RUN touch /var/run/nginx.pid && \
        chown -R $APP_USER:$APP_USER /var/run/nginx.pid

USER nginx
