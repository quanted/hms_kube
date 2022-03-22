FROM ghcr.io/quanted/mongodb:5.0.2
USER root

RUN dnf update -y
RUN yum update -y --cve CVE-2021-27219

RUN chown -R mongodb:mongodb /var/log /data/db
USER mongodb