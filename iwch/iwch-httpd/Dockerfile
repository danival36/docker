FROM registry.sb.upf.edu/info/iwch:10
#FROM ubuntu:bionic
MAINTAINER Daniel Valdes <daniel.valdes@upf.edu>

COPY startupScript.sh /usr/local/myscripts/startupScript.sh
RUN chmod 777 /usr/local/myscripts/startupScript.sh
EXPOSE 80
#CMD ["/usr/sbin/apache2ctl", "-D", "FOREGROUND"]
#CMD ["postfix", "start-fg"]
ENTRYPOINT [ "/usr/local/myscripts/startupScript.sh" ]
