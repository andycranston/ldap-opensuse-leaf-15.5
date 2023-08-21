#!/usr/bin/python3
#
# @(!--#) @(#) customise-slapd-conf.py, sversion 0.1.0, fversion 001, 21-august-2023
#
# customise a /etc/openldap/slapd.conf file
#

#
# imports
#

import sys
import os
import argparse

# ############################################################### #

def main():
    global progname

    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--infile',
                        default='/etc/openldap/slapd.conf',
                        help='name of existing slapd.conf file')

    parser.add_argument('-o', '--outfile',
                        required=True,
                        help='name of file to send preprocessed output to')

    args = parser.parse_args()

    try:
        ifile = open(args.infile, 'r', encoding='utf-8')
    except IOError:
        print('{}: unable to open file "{}" for reading'.format(progname, args.infile), file=sys.stderr)
        sys.exit(1)

    try:
        ofile = open(args.outfile, 'w', encoding='utf-8')
    except IOError:
        print('{}: unable to open file "{}" for writing'.format(progname, args.outfile), file=sys.stderr)
        sys.exit(1)

    for line in ifile:
        line = line.rstrip()

        words = line.split()

        if len(words) == 2:
            if (words[0] == '#moduleload') and (words[1] == 'back_mdb.la'):
                line = 'moduleload {}'.format(words[1])

        if len(words) == 2:
            if (words[0] == 'database'):
                line = 'database     mdb'

        if len(words) == 2:
            if (words[0] == 'suffix'):
                line = 'suffix       "dc=matrix,dc=lab"'

        if len(words) == 2:
            if (words[0] == 'rootdn'):
                line = 'rootdn       "cn=admin,dc=matrix,dc=lab"'

        if len(words) >= 2:
            if (words[0] == 'rootpw'):
                line = 'rootpw       "Only4Demos!"'

        print(line, file=ofile)

        if len(words) == 2:
            if (words[0] == '#moduleload') and (words[1] == 'back_bdb.la'):
                print('moduleload memberof.la', file=ofile)

    ofile.flush()
    ofile.close()
    ifile.close()

    return 0

# ############################################################### #

progname = os.path.basename(sys.argv[0])

sys.exit(main())

# end of file
