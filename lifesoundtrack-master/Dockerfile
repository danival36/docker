FROM ubuntu:16.04
MAINTAINER Life Soundtrack

RUN export DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y

ENV password 12345

# Install MySQL Server in a Non-Interactive mode. Default root password will be "root"

RUN apt-get install -y -q mysql-client


RUN apt-get install -y -q \
    python-pip \
    python-dev \
    build-essential \
    python-mysqldb \
    apache2 \
    libapache2-mod-wsgi \
    vim

RUN apt-get install -y -q libmysqlclient-dev

COPY . /app
WORKDIR /app
ENV HOME /app
RUN mkdir /var/www/log
RUN chown -R www-data /var/www/log


RUN pip install --upgrade pip
RUN pip install -r requirements.txt


COPY apache.conf /etc/apache2/sites-available/000-default.conf

EXPOSE 80
CMD apachectl -D FOREGROUND

