FROM ubuntu:16.04
RUN apt-get update
RUN apt-get install -y libapache2-mod-php7.0 php7.0-ldap php-common php-dev php-pear php-mbstring pkg-config php-mongodb 
RUN pecl install mongodb

ENV APACHE_RUN_USER www-data
ENV APACHE_RUN_GROUP www-data
ENV APACHE_LOG_DIR /var/log/apache2
ENV APACHE_LOCK_DIR /var/lock/apache2
ENV APACHE_PID_FILE /var/run/apache2.pid

# AllowOverride ALL
#RUN sed -i '264s#AllowOverride None#AllowOverride All#' /etc/apache2/httpd.conf
#Rewrite Moduble Enable
#RUN sed -i 's#\#LoadModule rewrite_module modules/mod_rewrite.so#LoadModule rewrite_module modules/mod_rewrite.so#' /etc/apache2/httpd.conf
# Document Root to /var/www/html/

#RUN mkdir -p /usr/share/sites/intranet-rp.s.upf.edu/shared/public

RUN rm /etc/apache2/sites-enabled/000-default.conf
COPY itourist.upf.edu.conf /etc/apache2/sites-enabled
COPY php.ini /etc/php/7.0/apache2
RUN a2enmod php7.0
RUN a2enmod rewrite
EXPOSE 80
CMD apachectl -D FOREGROUND

