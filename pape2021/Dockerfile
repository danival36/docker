#FROM wordpress:5.4.1-php7.3-apache
#FROM wordpress:5.9.2-php7.4
FROM php:7.4.29-apache

RUN apt-get update && \
	apt-get install -y  --no-install-recommends ssl-cert vim && \
	rm -r /var/lib/apt/lists/* && \
	a2enmod ssl && \
	a2ensite default-ssl
	
COPY 000-default.conf /etc/apache2/sites-available
