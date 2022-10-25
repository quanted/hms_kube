FROM nginx:1.23.1-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d

RUN apk update
RUN apk upgrade

ARG APP_USER=nginx

RUN mkdir /src

RUN chown -R $APP_USER:$APP_USER /src && chmod -R 755 /src && \
        chown -R $APP_USER:$APP_USER /var/cache/nginx && \
        chown -R $APP_USER:$APP_USER /var/log/nginx && \
        chown -R $APP_USER:$APP_USER /etc/nginx/conf.d
RUN touch /var/run/nginx.pid && \
        chown -R $APP_USER:$APP_USER /var/run/nginx.pid

USER root
