# Open LDAP on OpenSUSE

This repository has some useful shell scripts, a LDIF file and a Python
3 CGI script which will allow an Open LDAP server to be set up quickly
on OpenSUSE Leaf version 15.5

# ATTENTION!

I am not an expert on LDAP. This README document and the various files
in this repository may have incorrect or non-standard values.

My main motivation was to get a LDAP server up and running so devices on
a network (e.g. Raritan intelligent PDUs) can be configured to use LDAP
for demonstration purposes.

If you need to set up a LDAP server in a production environment then DO
NOT use this as the basis of your setup!

On the other hand if you just want to get a simple LDAP up and running
then continue reading.

# Assumptions and default values

This document makes the following assumptions and uses the following default values:

+ The OpenSUSE server has only one NIC (Network Interface Card)
+ The OpenSUSE server has NOT been previously configured to run Open LDAP
+ LDAP distinguished name dc=matrix,dc=lab will be used as the main organisation name
+ The LDAP environment will be unsecured and run on the default TCP port number 389
+ Secret password for configuration and LDAP access will be 'Only4Demos!' without the single quotes
+ Manager name of "admin" (i.e. cn=admin,dc=matrix,dc=lab)
+ You have appropriate access to run priviledged commands using the `sudo` command



# Install the packages

Run the following command:

```
sudo zypper install openldap2 openldap2-client openldap2-doc
```

to install the openldap2 server, the openldap2-client programs
(e.g. ldapsearch) and openldap2 documentation.

The openldap2-client programs may have been included when you initially
installed the operating system. If that is the case then the `zypper`
command will display a message.


# Edit the /etc/openldap/slapd.conf file

Create a backup of the `/etc/openldap/slapd.conf` file:

```
cd /etc/openldap
sudo cp -p slapd.conf slapd.conf.install
```

Edit the file `slapd.conf` file.

Change the line:

```
#moduleload back_mdb.la
```

to read:

```
moduleload back_mdb.la
```

After the line:

```
#moduleload back_bdb.la
```

add the line:

```
moduleload memberof.la
```

Change the lines:

```
suffix       "dc=my-domain,dc=com"
rootdn       "cn=Manager,dc=my-domain,dc=com"
```

to read:

```
suffix       "dc=matrix,dc=lab"
rootdn       "cn=admin,dc=matrix,dc=lab"
```

Change the line:

```
rootpw       secret
```

to read:

```
rootpw       "Only4Demos!"
```

Save changes.

Enable the slapd.service:

```
sudo systemctl enable slapd.service
```

Start the service:

```
sudo systemctl start slapd.service
```

Check the staus:

```
sudo systemctl status slapd.service
```

Output should be similar:

```
+ slapd.service - OpenLDAP Server Daemon
     Loaded: loaded (/usr/lib/systemd/system/slapd.service; enabled; vendor preset: disabled)
     Active: active (running) since Mon 2023-08-14 07:46:35 BST; 16s ago
    Process: 20528 ExecStart=/usr/lib/openldap/start (code=exited, status=0/SUCCESS)
   Main PID: 20540 (slapd)
      Tasks: 2 (limit: 4659)
     CGroup: /system.slice/slapd.service
             └─ 20540 /usr/sbin/slapd -h "ldap:///  ldapi:///" -f /etc/openldap/slapd.conf -u ldap -g ldap -o slp=off

Aug 14 07:46:35 opensuse systemd[1]: Starting OpenLDAP Server Daemon...
Aug 14 07:46:35 opensuse slapd[20528]: @(#) $OpenLDAP: slapd 2.4.46 $
                                               opensuse-buildservice@opensuse.org
Aug 14 07:46:35 opensuse slapd[20540]: slapd starting
Aug 14 07:46:35 opensuse start[20528]: Starting ldap-server
Aug 14 07:46:35 opensuse systemd[1]: Started OpenLDAP Server Daemon.
```

By default the firewall daemon `firewalld` will be blocking the LDAP TCP
port 389. Open up this port with

```
sudo firewall-cmd --zone=public --add-port=389/tcp --permanent
sudo firewall-cmd --reload
```

If the networking configuration is more complicated than a default
operating system installation with one NIC (Network Interface Card) then
the above `firewall-cmd` commands might need additional arguments.

Now run the `supplement_ldap_database.sh` script:

```
./supplement_ldap_database.sh
```

Output will be similar to:

```
adding new entry "dc=matrix,dc=lab"
adding new entry "ou=users,dc=matrix,dc=lab"
adding new entry "ou=roles,dc=matrix,dc=lab"
adding new entry "cn=Admin,ou=roles,dc=matrix,dc=lab"
adding new entry "cn=Operator,ou=roles,dc=matrix,dc=lab"
adding new entry "cn=readonly,ou=roles,dc=matrix,dc=lab"
adding new entry "uid=andyc,ou=users,dc=matrix,dc=lab"
adding new entry "uid=neila,ou=users,dc=matrix,dc=lab"
adding new entry "uid=dollyp,ou=users,dc=matrix,dc=lab"
```

At this stage an unsecured LDAP server is now running.

The details are:

+ Organisation "dc=matrix,dc=lab"
+ Organisational unit "ou=users,dc=matrix,dc=lab"
+ Organisational unit "ou=roles,dc=matrix,dc=lab"
+ Group of names "cn=Admin,ou=roles,dc=matrix,dc=lab"
+ Group of names "cn=Operator,ou=roles,dc=matrix,dc=lab"
+ Group of names "cn=readonly,ou=roles,dc=matrix,dc=lab"
+ InetOrgPerson "uid=andyc,ou=users,dc=matrix,dc=lab" with password "passAAAA1" and member of "cn=Admin,ou=roles,dc=matrix,dc=lab"
+ InetOrgPerson "uid=neila,ou=users,dc=matrix,dc=lab" with password "passNNNN1" and member of "cn=Operator,ou=roles,dc=matrix,dc=lab"
+ InetOrgPerson "uid=dollyp,ou=users,dc=matrix,dc=lab" with password "passDDDD1" adnd member of "cn=readonly,ou=roles,dc=matrix,dc=lab"

# Prove access is ok

From another host on the network that has the `ldapsearch` command run a command line similar to:

```
ldapsearch -D "cn=admin,dc=matrix,dc=lab" -w "Only4Demos!" -H ldap://192.168.1.80 -b "dc=matrix,dc=lab" -s sub "(objectclass=*)"
```

Change the IP address `192.168.1.80` to the IP address of the LDAP server.

If access is ok the first few lines of the `ldapsearch` command output will be:

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

and the last few lines will be:

```
# search result
search: 2
result: 0 Success

# numResponses: 10
# numEntries: 9
```

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

WARNING: Only use the `ldapwebpass.py` script on test system. It is NOT suitable for production systems. There
are several issues with it that could compromise system seurity. They include but are not limited to:

+ The master bind password is stored in clear text in the script
+ The subprocess function is used in the script - this is like using the "system" call in C programs
+ Very limited error checking

You have been warned!

----------------
End of README.md
