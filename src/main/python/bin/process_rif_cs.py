#!/usr/bin/env python
#JCU RIF-CS Pre-Processor
#Copyright (C) 2012  Nigel Bajema, James Cook University
#
#This program is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 2 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License along
#with this program; if not, write to the Free Software Foundation, Inc.,
#51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import sys, glob, os.path

sys.path.append(os.path.abspath(os.path.join(os.path.split(sys.argv[0])[0], "..")))
from jcu.tweak_rifcs import fix
from jcu import config, response, log
from argparse import ArgumentParser
from java.io import PrintWriter
from com.googlecode.fascinator.common import FascinatorHome

alerts = {}
execfile(os.path.abspath(os.path.join(os.path.split(sys.argv[0])[0], "..", "..", "config", "portal", "default", "redbox", "scripts", "hkjobs", "alerts.py")), globals(), alerts)
AlertsData = alerts["AlertsData"]

if __name__ == "__main__":

    argParse = ArgumentParser(description="Process the JCU RIF-CS imports")
    argParse.add_argument('-i','--inplace', dest='inplace', action='store_true', default=False, help='Update the files in place')
    argParse.add_argument('-o','--output', dest='output', action='store',  help='The output location, mutually exclusive with the inplace option.')
    argParse.add_argument('--redbox-protocol', nargs=1, dest='redbox_protocol', action='store', default="http", help='The protocol that redbox is running on, default: http.')
    argParse.add_argument('--redbox-host', nargs=1, dest='redbox_host', action='store', default="localhost", help='The hostname that redbox is running on, default: localhost.')
    argParse.add_argument('--redbox-port', nargs=1, dest='redbox_port', action='store', default=9000, help='The port that redbox is running on, default: 9000.')
    argParse.add_argument('--redbox-context', nargs=1, dest='redbox_context', action='store', default="researchdata", help='The context that redbox is running with, default: researchdata.')
    argParse.add_argument('--mint-protocol', nargs=1, dest='mint_protocol', action='store', default="http", help='The protocol that mint is running on, default: http.')
    argParse.add_argument('--mint-host', nargs=1, dest='mint_host', action='store', default="localhost", help='The hostname that mint is running on, default: localhost.')
    argParse.add_argument('--mint-port', nargs=1, dest='mint_port', action='store', default=9001, help='The port that mint is running on, default: 9001.')
    argParse.add_argument('--mint-context', nargs=1, dest='mint_context', action='store', default="nameauthority", help='The context that mint is running with, default: nameauthority.')


    argParse.add_argument('file', nargs='+', help='The RIF-CS Files to process (globs accepted)')
    args = argParse.parse_args()

    if args.output is not None and args.inplace:
        print "Options --inplace and --output cannot be used at the same time."
        argParse.print_help()
        sys.exit(5)
    output = None
    if args.output is not None:
        output = args.output

    for fl in args.file:
        for _file in glob.glob(fl):
            print "Processing: ", _file
            fix(_file, args, output)



