FROM ubuntu:14.04
MAINTAINER Daniel Valdes <daniel.valdes@upf.edu>

RUN apt-get update
RUN apt-get install -y		php5 \
				curl \
				libyaml-dev \
				libwww-perl \
				libxml-simple-perl \
				build-essential \
				apache2 \
				cron \
			        libapache2-mod-php5 \
				php5-dev \
                                php5-xmlrpc \
                                php-xml-parser \
				php5-mysql \
                                apache2 \
                                libxml2-dev \
                                apache2-utils \
				php5-mcrypt \
				php5-cgi \
				libdbi-perl \
				libxml-rss-feed-perl \
				libfeed-find-perl \
				libxml-feed-perl \
				libdbd-mysql-perl \
				php5-gd \
				vim 
 
 
				

#RUN ln -s /usr/bin/php5 /usr/bin/php
#RUN curl -sS https://getcomposer.org/installer | php5 -- --install-dir=/usr/bin --filename=composer 

#RUN cpan Test::Base
#RUN cpan Test::YAML
#RUN cpan YAML
#RUN cpan install Module::Build
#RUN cpan install Module::Runtime
#RUN cpan install Params::Util
#RUN cpan install Sub::Install
#RUN cpan install Module::Implementation
#RUN cpan install Package::DeprecationManager
#RUN cpan install Devel::GlobalDestruction
#RUN cpan install Class::Singleton
#RUN cpan install XML::LibXML
#RUN cpan install XML::DOM
#RUN cpan install HTML::Tree
#RUN cpan install HTML::TreeBuilder
#RUN cpan install DateTime


RUN cpan Module::Build
RUN cpan install XML::DOM
RUN cpan install HTML::Tree
RUN cpan install Data::Dump
RUN cpan install HTML::TreeBuilder
RUN cpan install DateTime
RUN cpan install DateTime::Locale
RUN cpan install DateTime::TimeZone
RUN cpan install Net::Twitter
RUN cpan install Twitter::API




 

RUN  rm -rf /var/cache/apk/*

ENV APACHE_RUN_USER www-data
ENV APACHE_RUN_GROUP www-data
ENV APACHE_LOG_DIR /var/log/apache2
ENV APACHE_LOCK_DIR /var/lock/apache2
ENV APACHE_PID_FILE /var/run/apache2.pid

# AllowOverride ALL
COPY 000-default.conf /etc/apache2/sites-enabled
RUN sed -i '264s#AllowOverride None#AllowOverride All#' /etc/apache2/apache2.conf
#Rewrite Moduble Enable
RUN sed -i 's#\#LoadModule rewrite_module modules/mod_rewrite.so#LoadModule rewrite_module modules/mod_rewrite.so#' /etc/apache2/apache2.conf
# Document Root to /var/www/html/

#Start apache
RUN mkdir -p /run/apache2

RUN mkdir -p /var/www/obneo/

VOLUME  /var/www/obneo/
WORKDIR  /var/www/obneo/

RUN mkdir -p /var/log/apache2

RUN touch /var/log/apache2/access.log
RUN touch /var/log/apache2/error.log


COPY php.ini /etc/php5/apache2/php.ini
RUN rm /usr/local/share/perl/5.18.2/DateTime/Format/Strptime.pm
COPY Strptime.pm /usr/local/share/perl/5.18.2/DateTime/Format


RUN mkdir -p /usr/iula/backup

RUN touch /var/log/cron.log


# l'apache l'executem com a command al composer 
# el crond l'executem com a command al composer 
#COPY crontab /etc

# executa el script del date 
COPY time.sh /root
# dona permisos al script
RUN chmod a+x /root/time.sh
# canvia la zona horaria a Madrid 
RUN echo Europe/Madrid > /etc/timezone

RUN a2enmod rewrite
#RUN a2enmod php5

EXPOSE 80
#EXPOSE 443




