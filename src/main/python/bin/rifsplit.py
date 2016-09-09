#!/usr/bin/env python
# Retrieved from http://www.redboxresearchdata.com.au/documentation/how-to/import-rif-cs-into-redbox
# Author: Duncan Dickinson

import sys, os
from xml.dom.minidom import parse, parseString, getDOMImplementation

OUTPUT_EXT = '.rif'
OUTPUT_DIR = 'output/'

if (not os.path.exists(OUTPUT_DIR)):
    os.mkdir(OUTPUT_DIR)

riftypes = ['collection','party','activity','service']

impl = getDOMImplementation()
dom = parse(sys.argv[1])
objects = dom.getElementsByTagName("registryObject")

for element in objects:
    newdoc = impl.createDocument(None, None, None)
    root = dom.documentElement.cloneNode(0)
    root.appendChild(element)
    newdoc.appendChild(root)
    
    for riftype in riftypes:
        if newdoc.getElementsByTagName(riftype):
            elementtype = riftype
            break
        
    #we'll use the key as the new filename
    key = newdoc.getElementsByTagName("key")[0].firstChild.nodeValue.replace('/','_')
    filename = OUTPUT_DIR + elementtype + '_' + key + OUTPUT_EXT
    print "Output file: " + filename
    xmlstr = newdoc.toprettyxml(indent= '  ', encoding='utf-8')
    f = open(filename , 'w')
    f.write(xmlstr)
    f.close()
