FROM nginx:stable

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d

ARG APP_USER=nginx

RUN mkdir /src

RUN chown -R $APP_USER:$APP_USER /src && chmod -R 755 /src && \
        chown -R $APP_USER:$APP_USER /var/cache/nginx && \
        chown -R $APP_USER:$APP_USER /var/log/nginx && \
        chown -R $APP_USER:$APP_USER /etc/nginx/conf.d
RUN touch /var/run/nginx.pid && \
        chown -R $APP_USER:$APP_USER /var/run/nginx.pid

USER nginx
