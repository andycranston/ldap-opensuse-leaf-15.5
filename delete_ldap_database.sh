#!/bin/bash
#

sudo systemctl stop slapd.service

for dbfile in data lock
do
  sudo mv /var/lib/ldap/${dbfile}.mdb /var/tmp/${dbfile}.`date '+%s'`
done

sudo systemctl start slapd.service

sudo systemctl status slapd.service

exit 0
