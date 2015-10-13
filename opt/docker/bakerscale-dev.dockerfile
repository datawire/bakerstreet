FROM ubuntu:14.04
MAINTAINER datawire.io <hello@datawire.io>

# install necessary system software
RUN apt-get -y update && apt-get install -y\
 curl\
 wget\
 gdebi\
 htop\
 lsof\
 netcat\
 net-tools\
 python-dev\
 python-pip\
 sysstat\
 tcpdump

# download necessary python libraries
RUN yes | pip install \
    docopt \
    flask

# install the directory and other essential datawire libraries
RUN curl -s https://packagecloud.io/install/repositories/datawire/staging/script.deb.sh | bash
RUN apt-get install -y datawire-proton

# copy then datawire packages into root directory
COPY datawire-common.deb datawire-directory.deb datawire-sherlock.deb datawire-watson.deb /

RUN gdebi -n /datawire-common.deb
RUN gdebi -n /datawire-directory.deb
RUN gdebi -n /datawire-sherlock.deb
RUN gdebi -n /datawire-watson.deb

# copy bakerscale utilities into root directory
COPY bakerscale.py\
 bakerscale_service.py\
 bakerscale_stats.py\
 /