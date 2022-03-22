#FROM ghcr.io/quanted/mongodb:5.0.2
#USER root
#
##RUN yum install -y yum-utils
##RUN yum-config-manager --set-enabled ubi-8-appstream-debug && \
##    yum-config-manager --set-enabled ubi-8-appstream-source && \
##    yum-config-manager --set-enabled ubi-8-baseos-debug && \
##    yum-config-manager --set-enabled ubi-8-baseos-source && \
##    yum-config-manager --set-enabled ubi-8-codeready-builder-debug && \
##    yum-config-manager --set-enabled ubi-8-codeready-builder-source
#
##RUN yum update -y --cve CVE-2021-27219
#
#RUN chown -R mongodb:mongodb /var/log /data/db
#USER mongodb

# ------------------------
FROM mongo:5.0.6
USER root

RUN apt update -y
RUN apt upgrade -y
RUN apt --only-upgrade install gosu

RUN chown -R mongodb:mongodb /var/log /data/db
USER mongodb