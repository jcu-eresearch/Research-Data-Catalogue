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
from argparse import ArgumentParser
from jcu import config, response, log
from com.googlecode.fascinator.common import FascinatorHome

alerts = {}
execfile(os.path.abspath(os.path.join(os.path.split(sys.argv[0])[0], "..", "..", "config", "portal", "default", "redbox", "scripts", "hkjobs", "alerts.py")), globals(), alerts)
AlertsData = alerts["AlertsData"]


if __name__ == "__main__":

    argParse = ArgumentParser(description="Process the JCU RIF-CS imports")
    argParse.add_argument('-a','--alerts', dest='alerts', action='store',  help='The alerts location.')
    argParse.add_argument('-m','--rifcs-map-file', nargs=1, dest='rmap', action='store', default=None, help='The location of the rifcs map file.')
    argParse.add_argument('-x','--xml-map-file', nargs=1, dest='xmap', action='store', default=None, help='The location of the xml map file.')
    argParse.add_argument('-p','--redbox-path', dest='path', nargs=1, action='store',  help='The base path of the ReDBoX Install')
    args = argParse.parse_args()

    if args.path is not None and os.path.exists(args.path[0]):
        fascinator_home = os.path.join(args.path[0], "home")

        FascinatorHome.setPath(fascinator_home)
        import json
        system = open(os.path.join(fascinator_home, "system-config.json"))
        system_data = json.load(system)
        system.close()

        _config = config(fascinator_home, system_data)
        output = _config.getString(None, ["alerts", "path"])
        if args.rmap is not None:
            system_data["alerts"]["xmlMaps"]["rif"] = args.rmap[0]
        if args.xmap is not None:
            system_data["alerts"]["xmlMaps"]["xml"] = args.xmap[0]

        if args.alerts is not None:
            system_data['alerts']['path'] = args.alerts

        #Imports may be due to the globals or locals in the alert import at top.
        import csv
        from com.googlecode.fascinator import HarvestClient
        from com.googlecode.fascinator.common import FascinatorHome
        from com.googlecode.fascinator.common import JsonObject
        from com.googlecode.fascinator.common import JsonSimple

        from java.io import File
        from java.io import FileInputStream
        from java.io import InputStreamReader
        from java.lang import Exception

        from org.dom4j import DocumentFactory
        from org.dom4j.io import SAXReader
        from org.json.simple import JSONArray
        from org.dom4j.xpath import DefaultNamespaceContext
        from org.dom4j.xpath import DefaultXPath
        from org.jaxen import SimpleNamespaceContext
        import csv
        import os
        import shutil
        import shutil
        import time
        alerts = AlertsData()
        alerts.__activate__({"log":log(), 'systemConfig': _config, 'response': response()})