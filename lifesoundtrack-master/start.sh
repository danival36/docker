#!/usr/bin/env bash

service mysql restart
chown :www-data /app
apache2ctl configtest
service apache2 restart
tail -f /var/log/apache2/error.log