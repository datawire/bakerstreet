FROM ubuntu:14.04
MAINTAINER datawire.io <hello@datawire.io>

RUN apt-get -y update && apt-get -y install curl python-dev python-docopt python-pip
RUN curl -s https://packagecloud.io/install/repositories/datawire/stable/script.deb.sh | bash
RUN apt-get -y -qq install datawire-directory datawire-sherlock datawire-watson
RUN pip install flask

COPY bakerscale.py bakerscale_service.py /