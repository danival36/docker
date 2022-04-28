#FROM wordpress:5.4.1-php7.3-apache
FROM php:7.2.2-apache

RUN apt-get update && \
	apt-get install -y  --no-install-recommends ssl-cert vim && \
	rm -r /var/lib/apt/lists/* && \
	a2enmod ssl && \
	a2ensite default-ssl
RUN mkdir -p /var/log/apache2/
RUN chmod -R 744 /var/log/apache2/
	
COPY 000-default.conf /etc/apache2/sites-available
COPY beforefirstwords.upf.edu.conf /etc/apache2/sites-available
COPY antesprimeraspalabras.upf.edu.conf /etc/apache2/sites-available

#RUN ln -s /etc/apache2/sites-available/000-default.conf /etc/apache2/sites-enabled/000-default.conf 
RUN ln -s /etc/apache2/sites-available/beforefirstwords.upf.edu.conf /etc/apache2/sites-enabled/beforefirstwords.upf.edu.conf
RUN ln -s /etc/apache2/sites-available/antesprimeraspalabras.upf.edu.conf /etc/apache2/sites-enabled/antesprimeraspalabras.upf.edu.conf

