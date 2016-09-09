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

from argparse import ArgumentParser
import sys, os.path, glob, json
from lxml import etree as ET
from lxml.etree import _Element

sys.path.append(os.path.abspath(os.path.join(os.path.split(sys.argv[0])[0], "..")))
from jcu import config_helper

namespace = {"rif": "http://ands.org.au/standards/rif-cs/registryObjects"}
from pprint import pprint

def remove_used_nodes(map, tree):
#    print map, tree
    for i in map:
        if isinstance(map[i],  dict):
            for n in tree.xpath(i, namespaces=namespace):
                remove_used_nodes(map[i], n)

        else:
            n = tree.xpath(i, namespaces=namespace)
            if isinstance(n, list):
                for nn in n:
                    if isinstance(nn, _Element):
#                        nn.getparent().remove(nn)
                        nn.text = ""
                    else:
                        if nn.is_attribute:
                            del nn.getparent().attrib[nn.attrname]
                        else:
                            print "__________________"

            elif isinstance(n, _Element):
                print i, n
            else:
                print "---------------->",n.__class__




if __name__ == "__main__":
    default_redbox_path = os.path.abspath(os.path.join(os.path.split(sys.argv[0])[0], "..", "..", "config", "home", "alerts", "config", "rifXmlMap.json"))
    argParse = ArgumentParser(description="Process the JCU RIF-CS imports")
    argParse.add_argument('-p','--map-path', dest='path', nargs=1, action='store', default=default_redbox_path, help='The map file to use, default: '+default_redbox_path)
    argParse.add_argument('file', nargs='+', help='The RIF-CS Files to process (globs accepted)')
    args = argParse.parse_args()

    map_file = open(args.path)
    map = config_helper(json.load(map_file))
    map_file.close()

    for fl in args.file:
        for _file in glob.glob(fl):
            print "Processing: ", _file
            tree = ET.parse(_file)
            remove_used_nodes(map.mappings, tree)
            tree.write(sys.stdout, encoding='utf-8')
            print ""
            print "============================================================================="
