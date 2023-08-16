#!/bin/bash
#

ldapadd -x -D cn=admin,dc=matrix,dc=lab -w 'Only4Demos!' -f matrix.lab.ldif

exit $?
