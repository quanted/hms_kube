FROM ghcr.io/quanted/mongodb:5.0.2
USER root

RUN yum update -y --cve CVE-2021-27219

RUN yum update -y
RUN yum upgrade -y

RUN chown -R mongodb:mongodb /var/log /data/db
USER mongodb

