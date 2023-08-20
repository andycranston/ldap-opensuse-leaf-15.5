#!/usr/bin/python3

#
# @(#) @(!--#) ldapwebpass.py, version 002, 15-august-2023
#
# web page to change LDAP user passwords using the ldappasswd command
#

##############################################################################

#
# imports
#

import sys
import os
import cgi
import cgitb 
import html
import subprocess

##############################################################################

#
# constants
#

LDAP_IP = '192.168.1.80'
DC_BASE = 'dc=matrix,dc=lab'
BIND_NAME = 'cn=admin' + ',' + DC_BASE
BIND_PASS = 'Lmob5Wvnlh!'

CSS = '''
body {
  font-family: Arial, Verdana, Helvectica, sans-serif;
  background-color: white;
  color: black;
}

h1, h2, h3, h4, h5, h6 {
  border-bottom-style: solid;
  border-color: lightgrey;
  border-width: thin;
}

table {
  margin-left: 100px;
}

input[type=submit] {
  padding: 8px 30px;
  background-color: linen;
}

pre {
  font-family: "Lucinda Console", monospace;
  background-color: linen;
  color: black;
  margin-left: 100px;
  margin-right: 100px;
  padding: 5px;
}

p {
  margin-left: 100px;
}
'''


##############################################################################

def rot(c, b, l):
    bo = ord(b)
    co = ord(c)

    diff = co - bo

    return chr(bo + l - 1 - diff)

##############################################################################


def defudge(s):
    d = ''

    for c in s:
        if c.isdigit():
            d += rot(c, '0', 10)
        elif c.islower():
            d += rot(c, 'a', 26)
        elif c.isupper():
            d += rot(c, 'A', 26)
        else:
            d += c

    return d

##############################################################################

def validusername(u):
    validflag = True

    if u == '':
        validflag = False
    elif not (u[0].islower()):
        validflag = False
    else:
        for c in u[1:]:
            if not (c.islower() or c.isdigit()):
                validflag = False
                break

    return validflag
        
##############################################################################

def validpassword(p):
    validflag = True

    if p == '':
        validflag = False
    else:
        for c in p:
            if not (c.isupper() or c.islower() or c.isdigit() or (c in '.-_+=:./')):
                validflag = False
                break

    return validflag
        
##############################################################################

#
# main
#

# switch on cgi troubleshooting
cgitb.enable()

form = cgi.FieldStorage()

bindpass     = form.getfirst('bindpass', '')
username     = form.getfirst('username', '')
password     = form.getfirst('password', '')
confirmp     = form.getfirst('confirmp', '')

reset        = form.getfirst('reset', '')

title = 'LDAP User Password Reset'

print('Content-type: text/html')
print('')

print('<head>')
print('<title>{}</title>'.format(html.escape(title)))

print('<style>')
print(CSS)
print('</style>')

print('</head>')

print('<body>')

print('<h1>{}</h1>'.format(html.escape(title)))

print('<form method="post" action="ldapwebpass.py">')

print('<table>')

print('<td>Master bind password:</td> <td><input type="password" name="bindpass" value="{}"></td>'.format(html.escape(bindpass, quote=False)))

print('<tr>')

print('<td>Existing Username:</td>    <td><input type="text"     name="username" value="{}"></td>'.format(html.escape(username, quote=False)))

print('<tr>')

print('<td>New Password:</td>         <td><input type="password" name="password" value="{}"></td>'.format(html.escape(password, quote=False)))

print('<tr>')

print('<td>Confirm Password:</td>     <td><input type="password" name="confirmp" value="{}"></td>'.format(html.escape(confirmp, quote=False)))

print('</table>')

print('<p>')

print('<td><input type="submit" name="reset" value="Reset LDAP Password"></td>')

print('</p>')

print('</form>')

if reset != '':
    print('<pre>')

    if ((bindpass == '') or (username == '') or (password == '') or (confirmp == '')):
        print('All fields are mandatory')
    elif bindpass != defudge(BIND_PASS):
        print('Master bind password incorrect')
    elif (not validusername(username)):
        print('Invalid username')
    elif (password != confirmp):
        print('Passwords are not identical')
    elif (not validpassword(password)):
        print('Invalid password')
    else:
        cmd = 'ldappasswd -x -D {} -w {} -H ldap://{} -s {} uid={},ou=users,{}'.format(BIND_NAME, defudge(BIND_PASS), LDAP_IP, password, username, DC_BASE)

        s = subprocess.run(cmd, shell=True, capture_output=True)

        if s.returncode != 0:
            print('Password change failed - return code from ldappasswd command is {}'.format(s.returncode))
        else:
            print('Password change appears to be successful')

        if len(s.stderr) != 0:
            for c in s.stderr:
                if c == '\n':
                    print('')
                else:
                    print(chr(c), end='')

        if len(s.stdout) != 0:
            for c in s.stdout:
                if c == '\n':
                    print('')
                else:
                    print(chr(c), end='')

    print('</pre>')

print('</body>')
