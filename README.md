# Open LDAP on OpenSUSE

Running an open LDAP server on OpenSUSE Leaf 15.5.

# Assumptions and default values

This document makes the following assumptions and uses the following default values:

+ The LDAP server has only one NIC (Network Interface Card)
+ The LDAP server has NOT been configured to run open LDAP in the past
+ LDAP domain name "matrix.lab" (i.e. dc=matrix,dc=lab)
+ Secret password for configuration and LDAP access: Broadbus1
+ Manager name of "admin" (i.e. cn=admin,dc=matrix,dc=lab)


# Get before file listings

Run these commands:

```
cd
sudo find / -type f -print | sort > files.b4
sudo find / -type d -print | sort > dirs.b4
sudo find / -type l -print | sort > symlinks.b4
```

# Install the packages

The following command:

```
sudo zypper install openldap2 openldap2-client openldap2-doc
```

will install the openldap2 server, the openldap2-client programs (e.g. ldapsearch) and openldap2 documentation.

The openldap2-client programs may have been included when you initially installed the operating system. If that is
the case then the `zypper` command will display a message.

# Get after file listings

Run these commands:

```
cd
sudo find / -type f -print | sort > files.after
sudo find / -type d -print | sort > dirs.after
sudo find / -type l -print | sort > symlinks.after
```

# Edit the /etc/openldap/slapd.conf file

Take a backup of the `/etc/openldap/slapd.conf` file:

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
rootpw       Broadbus1
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
```

If the networking configuration is more complicated than a default
operating system installation with one NIC (Network Interface Card) then
the above `firewall-cmd` command line might need additional arguments.

# Display all the LDAP database content for dc=matrix,dc=lab

Running this command:

```
ldapsearch -D "cn=admin,dc=matrix,dc=lab" -w Broadbus1 -H ldap://localhost -b "dc=matrix,dc=lab" -s sub "(objectclass=*)"
```

on the OpenSUSE ldap server will display all LDAP entries in and under dc=matrix,dc=lab.

Example output for no entries:

```
# extended LDIF
#
# LDAPv3
# base <dc=matrix,dc=lab> with scope subtree
# filter: (objectclass=*)
# requesting: ALL
#

# search result
search: 2
result: 32 No such object

# numResponses: 1
```

# Set up minimal dc=matrix,dc=lab entries

Obtain a copy of the file:

```
matrix.lab.ldif
```

Run this command:

```
ldapadd -x -D cn=admin,dc=matrix,dc=lab -w Broadbus1 -f matrix.lab.ldif
```

A successful run should display output similar to:

```
adding new entry "dc=matrix,dc=lab"
adding new entry "ou=users,dc=matrix,dc=lab"
adding new entry "ou=roles,dc=matrix,dc=lab"
adding new entry "cn=admin,ou=roles,dc=matrix,dc=lab"
adding new entry "cn=full,ou=roles,dc=matrix,dc=lab"
adding new entry "cn=readonly,ou=roles,dc=matrix,dc=lab"
adding new entry "uid=andyc,ou=users,dc=matrix,dc=lab"
adding new entry "uid=neila,ou=users,dc=matrix,dc=lab"
adding new entry "uid=dollyp,ou=users,dc=matrix,dc=lab"
```

The LDAP database now has entries to allow it to be used for some very basic
user authentication tests.

# Delete database

To delete the LDAP database and start again do the following:

```
sudo systemctl stop slapd.service
sudo mv /var/lib/ldap/data.mdb /var/tmp
sudo mv /var/lib/ldap/lock.mdb /var/tmp
sudo systemctl start slapd.service
sudo systemctl status slapd.service
```

ATTENTION: only delete the database if it has become corrupted 
beyond repair.

# Add a dummy organisational unit (OU) entry

Create a file called:

```
ou_people.ldif
```

with the following content:

```
dn: dc=my-domain,dc=com
objectClass: top
objectClass: dcObject
objectClass: organization
dc: my-domain
o : my-domain

dn: ou=people,dc=my-domain,dc=com
objectClass: organizationalUnit
ou: people
```

Run the ldapadd command as follows:

```
ldapadd -x -D cn=Manager,dc=my-domain,dc=com -w secret -f ou_people.ldif
```

Output should be:

```
adding new entry "dc=my-domain,dc=com"

adding new entry "ou=people,dc=my-domain,dc=com"
```

Now run:

```
ldapsearch -D "cn=Manager,dc=my-domain,dc=com" -w secret -H ldap://localhost -b "dc=my-domain,dc=com" -s sub "(objectclass=*)"
```

This command displays all the entries at and under `"dc=my-domain,dc=com"`.

# Start over

Stop the slapd service:

```
sudo systemctl stop slapd.service
```

Disable the slapd service:

```
sudo systemctl disablep slapd.service
```

Clear out the MDB database:

```
sudo -s
cd /var/lib/ldap
mv data.mdb lock.mdb /var/tmp
Ctrl^D
```


# Add TCP port 389 to firewall

By default 

```
sudo firewall-cmd --zone=public --add-port=389/tcp --permanent
```

------------------------

End of document
