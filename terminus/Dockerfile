FROM ubuntu:14.04
MAINTAINER Daniel Valdes <daniel.valdes@upf.edu>

RUN apt-get update
RUN apt-get install -y          php5 \
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
				libapache-session-perl \
				libapache2-authcookie-perl \
				libapache2-mod-perl2 \
				libapache2-mod-perl2-dev \
				libapache2-mod-perl2-doc \
				libapache2-reload-perl \
				libapache2-request-perl \
				libapache2-sitecontrol-perl \
                                libapache-dbi-perl \
                                libswitch-perl \
                                libapache2-mod-wsgi \
                                build-essential \
                                xsltproc \
                                libclass-accessor-perl \
                                vim \
				htmldoc \
 				sendmail \
				html2text \
			        libany-moose-perl \
				pdftohtml \
				libgd-perl \
				libpdf-api2-simple-perl \
				libconfig-yaml-perl \
				unzip\
				antiword

RUN cpan Module::Build
RUN cpan install	   Algorithm::Diff
RUN cpan install	   Alvis::Convert
RUN cpan install	   Alvis::Pipeline
RUN cpan install	   Apache::DBI
RUN cpan install RTF::TEXT::Converter
RUN cpan HTML::Template
RUN cpan HTML::HTMLDoc::PDF
RUN cpan IO::File

COPY 000-default.conf /etc/apache2/sites-available/000-default.conf

# Update the PHP.ini file, enable <? ?> tags and quieten logging.

RUN sed -i "s/short_open_tag = Off/short_open_tag = On/" /etc/php5/apache2/php.ini
RUN sed -i "s/error_reporting = .*$/error_reporting = E_ERROR | E_WARNING | E_PARSE/" /etc/php5/apache2/php.ini

# Actualitzem la data

COPY timezone /etc
RUN rm -rf /etc/localtime
RUN dpkg-reconfigure -f noninteractive tzdata


RUN a2enmod cgi
ADD  5.18.2.tar.gz /usr/local/share/perl/
ADD  cgi-bin.tar.gz /usr/lib/
ADD TreeTagger.tar.gz /usr/local/ 
EXPOSE 80


