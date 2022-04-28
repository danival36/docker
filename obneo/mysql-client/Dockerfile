FROM ubuntu:14.04
MAINTAINER Daniel Valdes <daniel.valdes@upf.edu>

RUN apt-get update
RUN apt-get install -y          apache2 \
				mysql-client

COPY mysql-var.sh mysql-var.sh
COPY script.sql script.sql
