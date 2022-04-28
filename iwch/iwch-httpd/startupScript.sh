#!/bin/bash 
sleep 5
/usr/sbin/postfix start 
sleep 5
/usr/sbin/apache2ctl  -D FOREGROUND 
