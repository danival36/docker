FROM ubuntu:16.04
MAINTAINER Life Soundtrack
ENV TZ=Europe/Madrid
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

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
    php\ 
    libapache2-mod-php \
    php-mysql \
    vim

RUN apt-get install -y -q libmysqlclient-dev

COPY . /app
WORKDIR /app
ENV HOME /app
RUN mkdir /var/www/log
RUN chown -R www-data /var/www/log
RUN a2enmod proxy
RUN a2enmod proxy_http
RUN a2enmod proxy_balancer
RUN a2enmod lbmethod_byrequests

#RUN pip install --upgrade pip
#RUN pip install -r requirements.txt


COPY 000-default.conf /etc/apache2/sites-available/000-default.conf

EXPOSE 80
CMD apachectl -D FOREGROUND

