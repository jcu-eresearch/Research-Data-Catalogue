import os
import json
import argparse

from os.path import join, getsize
from xml.etree import ElementTree as etree

##
# This data fix program is designed to clean some issues with the EnMaSSe data harvest.
# It is to run against the original xml files that were used to harvest the data into ReDBox using the newAlerts processing.

# 1. dc:accessRights.skos:prefLabel and dc_accessRights - the text is replaced as per below in the code
# 2. For all child records, the fields "dc:biblioGraphicCitation.dc:hasPart.bibo:Website.dc:identifier" and "bibo:Website.1.dc:identifier"
#    are to have '/data' appended to the end of the value. e.g. https://researchdata.jcu.edu.au/enmasse/1016 should be https://researchdata.jcu.edu.au/enmasse/1016/data 
# 3. For the parent records, the fields "dc:biblioGraphicCitation.dc:hasPart.bibo:Website.dc:identifier" and "bibo:Website.1.dc:identifier"
#    are to be set to https://research.jcu.edu.au/enmasse/search/id_list=project_<ID> where <ID> is the id of the parent record. e.g. 1, 2 or 3.

# This fix only needs to be executed once.
 
parser = argparse.ArgumentParser(description='Perform data cleanup of EnMaSSe')
parser.add_argument('storagePath', metavar='storagePath', help='The path of the storage folder within ReDBox.')

print 'Using the following path to process redbox cleanup: ', parser.parse_args().storagePath

count = 0

for root, dirs, files in os.walk(parser.parse_args().storagePath):
    for fileName in files:
         if (fileName.endswith(".xml")):
            #print os.path.join(root, 'metadata.json')
            try:
                 xmldoc = etree.parse(os.path.join(root, fileName))
                 saveFile = False

                 #For all records, update the access_rights
                 accessRights = xmldoc.find("access_rights")
                 if  (accessRights.text == "Contact Manager"):
                     accessRights.text = "Restricted access. Login authentication is required to access the data - please contact the data manager or nominated primary contact to negotiate access. If you have difficulty, please contact researchdata@jcu.edu.au for assistance."
                     saveFile = True

                 # Process the parent records.
                 if  ((xmldoc.find("redbox_identifier").text == "jcu.edu.au/collection/enmasse/1") or
                     (xmldoc.find("redbox_identifier").text == "jcu.edu.au/collection/enmasse/2") or
                     (xmldoc.find("redbox_identifier").text == "jcu.edu.au/collection/enmasse/3")):
                     citationUrl = xmldoc.find("citation_url")
                     citationUrl.text = "https://research.jcu.edu.au/enmasse/search/dataset/id_list=project_" + xmldoc.find("redbox_identifier").text[-1:]
                     dataStorageLocation = xmldoc.find("data_storage_location")
                     dataStorageLocation.text = "https://research.jcu.edu.au/enmasse/search/dataset/id_list=project_" + xmldoc.find("redbox_identifier").text[-1:]
                     saveFile = True

                 #Process the child records.
                 if  ((xmldoc.find("redbox_identifier").text != "jcu.edu.au/collection/enmasse/1") and
                     (xmldoc.find("redbox_identifier").text != "jcu.edu.au/collection/enmasse/2") and
                     (xmldoc.find("redbox_identifier").text != "jcu.edu.au/collection/enmasse/3")):
                     citationUrl = xmldoc.find("citation_url")
                     dataStorageLocation = xmldoc.find("data_storage_location")
                     if  (citationUrl.text.endswith("/data") ==  False):
                         citationUrl.text = citationUrl.text + "/data"
                         saveFile = True
                     if  (dataStorageLocation.text.endswith("/data") ==  False):
                         dataStorageLocation.text = dataStorageLocation.text + "/data"
                         saveFile = True

                 if  saveFile:
                     xmldoc.write(os.path.join(root, fileName))
                     count = count + 1
                     print("Record processed: " + str(count) + " " + os.path.join(root, fileName))
            except ValueError as e:
                print ("Oops, there is a dodgy one: ", os.path.join(root, fileName)) 
                print ("ValueError: ", e)