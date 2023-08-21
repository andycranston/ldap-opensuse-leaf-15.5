#!/bin/bash
#
# @(!--#) @(#) uninstall.sh, sversion 0.1.0, fversion, 21-august-2023
#
# uninstall OpenLDAP from an OpenSUSE Leaf 15.5 server
#

set -u

#
# Main
#

PATH=/bin:/usr/bin:/sbin:/usr/sbin
export PATH

progname=`basename $0`

user=`id | cut -d'(' -f2 | cut -d')' -f1`

if [ "$user" != "root" ]
then
  echo "$progname: must run with root priviledge - e.g: sudo ./$progname" 1>&2
  exit 1
fi

echo "This script will uninstall OpenLDAP packages,"
echo "LDAP database and *ALL* LDAP configuration files"
echo
echo "Do you want to continue (y/n):"

read response

case "$response" in
  y|Y|yes|YES|Yes)
    /bin/true
    ;;
  *)
    echo "Exiting script"
    exit 1
    ;;
esac

echo "Stopping slapd.service"
sudo systemctl stop slapd.service

echo "Disabling slapd.service"
sudo systemctl disable slapd.service

echo "Removing LDAP packages"
sudo --non-interactive zypper remove openldap2 openldap2-doc

if [ -d /etc/openldap ]
then
  echo "Moving /etc/openldap to /var/tmp"
  sudo mv /etc/openldap /var/tmp/etc-openldap.`date '+%s'`
fi

if [ -d /var/lib/ldap ]
then
  echo "Moving /var/lib/ldap to /var/tmp"
  sudo mv /var/lib/ldap /var/tmp/var-lib-openldap.`date '+%s'`
fi

echo "Removing firewall port 389"
sudo firewall-cmd --zone=public --remove-port=389/tcp --permanent

echo "Reloading firewalld daemon"
sudo firewall-cmd --reload

echo "Finished"

exit 0
