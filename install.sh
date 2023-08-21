#!/bin/bash
#
# @(!--#) @(#) install.sh, sversion 0.1.0, fversion, 21-august-2023
#
# install OpenLDAP from an OpenSUSE Leaf 15.5 server
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

echo "This script will install OpenLDAP packages,"
echo "and set up a simple LDAP database"
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

echo "Installing LDAP packages"
sudo zypper --non-interactive install openldap2 openldap2-client openldap2-doc

if [ -r /etc/openldap/slapd.conf ]
then
  echo "Creating a backup copy of /etc/openldap/slapd.conf"
  sudo cp -p /etc/openldap/slapd.conf /etc/openldap/slapd.conf.install
fi

echo "Customising /etc/openldap/slapd.conf"
cp -p customise-slapd-conf.py /tmp
sudo /tmp/customise-slapd-conf.py --outfile /tmp/slapd.conf.$$







echo "Finished"

exit 0
