#!/bin/bash
#
# @(!--#) @(#) install.sh, sversion 0.1.0, fversion, 21-august-2023
#
# install OpenLDAP on to an OpenSUSE Leaf 15.5 server
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

echo "Adding firewall rule for port 389"
sudo firewall-cmd --zone=public --add-port=389/tcp --permanent

echo "Reloading firewall daemon"
sudo firewall-cmd --reload

if [ -r /etc/openldap/slapd.conf ]
then
  echo "Creating a backup copy of /etc/openldap/slapd.conf"
  sudo cp -p /etc/openldap/slapd.conf /etc/openldap/slapd.conf.`date '+%s'`
fi

echo "Customising /etc/openldap/slapd.conf"
cp -p customise-slapd-conf.py /tmp
sudo /tmp/customise-slapd-conf.py --outfile /tmp/slapd.conf.$$
if [ $? -ne 0 ]
then
  echo "$progname: problem creating a customised slapd.conf file" 1>&2
  exit 1
fi
cp /tmp/slapd.conf.$$ /etc/openldap/slapd.conf

echo "Enabling slapd.service"
sudo systemctl enable slapd.service

echo "Starting slapd.service"
sudo systemctl start slapd.service

echo "Adding LDAP entries"
ldapadd -x -D cn=admin,dc=matrix,dc=lab -w 'Only4Demos!' -f matrix.lab.ldif

echo "Determining first IPv4 address on this host"
firstipv4=`ip addr | grep '^    inet [0-9]' | grep -v '^    inet 127.0.0' | head -n 1 | awk '{ print $2 }' | cut -d/ -f1`
if [ "$firstipv4" == "" ]
then
  echo "$progname: unable to determine the first IPv4 address in this host" 1>&2
  exit 1
fi
echo "$firstipv4"

echo "Run this command from another host to test this LDAP server:"
echo
echo "  ldapsearch -D cn=admin,dc=matrix,dc=lab -w 'Only4Demos!' -H ldap://$firstipv4 -b dc=matrix,dc=lab -s sub '(objectclass=*)'"
echo

echo "Finished"

exit 0
