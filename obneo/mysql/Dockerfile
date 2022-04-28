FROM mysql:5.7
MAINTAINER Daniel Valdes <daniel.valdes@upf.edu>

COPY timezone /etc
RUN rm -rf /etc/localtime
RUN dpkg-reconfigure -f noninteractive tzdata

EXPOSE 3306 33060


