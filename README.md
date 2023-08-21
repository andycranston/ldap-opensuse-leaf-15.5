# OpenLDAP on OpenSUSE Leaf 15.5

This repository has a shell script called `install.sh` and other files
which will get OpenLDAP installed and configured in less than a minute.

This is for a server running OpenSUSE Leaf 15.5 only.

# Assumptions

This document and the programs/files in the repositity make the following assumptions:

+ The OpenSUSE server has only one NIC (Network Interface Card)
+ The OpenSUSE server has NOT been previously configured to run Open LDAP
+ You have appropriate access to run priviledged commands using the `sudo` command
+ The LDAP environment will be unsecured (no digital certificate) and will run on the default TCP port number 389

# Quick start

Run the `install.sh` script as follows:

```
sudo ./install.sh
```

When prompted with:

```
This script will install OpenLDAP packages,
and set up a simple LDAP database

Do you want to continue (y/n):
```

respond by typing:

```
y
```

and pressing return.

Once the `install.sh` script completes an unsecured LDAP server is now running on TCP port 389.

The last few lines of output will be similar to:

```
Run this command from another host to test this LDAP server:

  ldapsearch -D cn=admin,dc=matrix,dc=lab -w 'Only4Demos!' -H ldap://192.168.1.82 -b dc=matrix,dc=lab -s sub '(objectclass=*)'

Finished
```

Login to another host on the network that has the `ldapsearch` command and run command line as displayed. If everything is working
as expected the first few lines of output should be similar to:

```
# extended LDIF
#
# LDAPv3
# base <dc=matrix,dc=lab> with scope subtree
# filter: (objectclass=*)
# requesting: ALL
#

# matrix.lab
dn: dc=matrix,dc=lab
objectClass: top
objectClass: dcObject
objectClass: organization
dc: matrix
o: matrix
```

and the last few lines should be:

```
# search result
search: 2
result: 0 Success

# numResponses: 10
# numEntries: 9
```

Congratulations! You now have a LDAP server running in unsecured mode on TCP port 389.

# LDAP values and entries

The following LDAP values have been set:

+ Bind distinguished name: cn=admin,dc=matrix,dc=lab
+ Bind password: Only4Demos!

The following LDAP entries will have been created:

+ Organisation: dc=matrix,dc=lab
+ Organisational unit: ou=users,dc=matrix,dc=lab
+ Organisational unit: ou=roles,dc=matrix,dc=lab
+ Group of names: cn=Admin,ou=roles,dc=matrix,dc=lab
+ Group of names: cn=Operator,ou=roles,dc=matrix,dc=lab
+ Group of names: cn=readonly,ou=roles,dc=matrix,dc=lab
+ InetOrgPerson: uid=andyc,ou=users,dc=matrix,dc=lab with password passAAAA1 and member of cn=Admin,ou=roles,dc=matrix,dc=lab
+ InetOrgPerson: uid=neila,ou=users,dc=matrix,dc=lab with password passNNNN1 and member of cn=Operator,ou=roles,dc=matrix,dc=lab
+ InetOrgPerson: uid=dollyp,ou=users,dc=matrix,dc=lab with password passDDDD1 adnd member of cn=readonly,ou=roles,dc=matrix,dc=lab

# Changing LDAP entries

From this point existing entries could be modified or deleted. New
entries can be added.

Use the command line utilities such as `ldapmodify` and `ldapadd` or
consider using a LDAP directory browser.  Just use your preferred internet
search engine and search for "ldap browser". Plenty to choose from.

# Starting again

To set the LDAP database back to a known state run:

```
./delete_ldap_database.sh
./supplement_ldap_database.sh
```

The `delete_ldap_database.sh` script will likely prompt you for your password to enable sudo access.

WARNING: This will delete all the current LDAP entries.

# ATTENTION!!!

I am not an expert on LDAP. This README document and the various files
in this repository may have incorrect or non-standard values.

My main motivation was to get a LDAP server up and running so devices on
a network (e.g. Raritan intelligent PDUs) can be configured to use LDAP
for demonstration purposes.

If you need to set up a LDAP server in a production environment then DO
NOT use this as the basis of your setup!

# The ldapwebpass.py Python 3 CGI script

The `ldapwebpass.py` Python 3 CGI script can be added to a web server which has CGI support enables, allows Python 3 programs to run under CGI
and has access to the `ldappasswd` command. The web server also requires network access to the LDAP server via TCP port 389.

After copying the script to the web server edit the script and change the line near the top of the script that begins:

```
LDAP_IP =
```

Change the line so it has the IP address of the LDAP server.

For example if the LDAP server is running on IP address `192.168.1.80` then change the line to read:

```
LDAP_IP = '192.168.1.80'
```

WARNING: Only use the `ldapwebpass.py` script on test systemis. It is `NOT` suitable for production systems. There
are several issues with it that could compromise system seurity. They include but are not limited to:

+ The master bind password is stored in clear text in the script
+ The subprocess function is used in the script - this is like using the "system" call in C programs
+ Very limited error checking

You have been warned!

----------------
End of README.md
