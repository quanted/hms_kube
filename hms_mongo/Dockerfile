FROM mongo:latest

RUN apt-get update
RUN apt-get -y upgrade

# Uninstall GO
RUN apt-get remove golang-go
RUN apt-get remove --auto-remove golang-go
RUN rm -rvf /usr/local/go
#
## Install newer version of GO
#RUN wget https://dl.google.com/go/go1.17.8.linux-amd64.tar.gz
#RUN tar -xvf go1.17.8.linux-amd64.tar.gz
#RUN mv go /usr/local

#ENV GOROOT=/usr/local/go
#ENV GOPATH=$HOME/go
#ENV PATH=$GOPATH/bin:$GOROOT/bin:$PATH

#RUN go version

RUN chown -R mongodb:mongodb /var/log /data/db
USER mongodb

