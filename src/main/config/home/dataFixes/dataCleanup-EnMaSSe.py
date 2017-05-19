import os
import json
import argparse

from os.path import join, getsize

##
# This data fix program is designed to clean some issues with the EnMaSSe data harvest.

# 1. dc:accessRights.skos:prefLabel and dc_accessRights - the text is replaced as per below
# 2. For all child records, the fields "dc:biblioGraphicCitation.dc:hasPart.bibo:Website.dc:identifier" and "bibo:Website.1.dc:identifier"
#    are to have '/data' appended to the end of the value. e.g. https://researchdata.jcu.edu.au/enmasse/1016 should be https://researchdata.jcu.edu.au/enmasse/1016/data 
# 3. For the parent records, the fields "dc:biblioGraphicCitation.dc:hasPart.bibo:Website.dc:identifier" and "bibo:Website.1.dc:identifier"
#    are to be set to https://research.jcu.edu.au/enmasse/search/id_list=project_<ID> where <ID> is the id of the parent record. e.g. 1, 2 or 3.

# This fix only needs to be executed once.
# 1. Check the queues in Mint and ReDBox. If they are empty, stop both servers. 
# 2. Back up the 'storage' folder in 'RedBox'
# 3. Run this script against redbox/storage folder.
# 4. Restart Mint and ReDBox.
# 5. Log into the ReDBox as admin, change to the 'Published' view, and 'reharvest' everything..wait, it takes a while.
#
 
parser = argparse.ArgumentParser(description='Perform data cleanup of EnMaSSe')
parser.add_argument('storagePath', metavar='storagePath', help='The path of the storage folder within ReDBox.')

print 'Using the following path to process redbox cleanup: ', parser.parse_args().storagePath

count = 0

for root, dirs, files in os.walk(parser.parse_args().storagePath):
    for fileName in files:
         if (fileName.endswith(".xml.1.tfpackage")):
            #print os.path.join(root, 'metadata.json')
            try:
                 file = open(os.path.join(root, fileName), 'r+')
                 jsonData = json.load(file)
                 file.close()
                 saveFile = False
                 count = count + 1
                 ##updating the access Rights for all EnMaSSe records
                 if  "dc:accessRights.skos:prefLabel" in jsonData:
                     if  (jsonData["dc:accessRights.skos:prefLabel"] == "Contact Manager"):
                         print ("    Replacing prefLabel")
                         jsonData["dc:accessRights.skos:prefLabel"] = "Restricted access. Login authentication is required to access the data - please contact the data manager or nominated primary contact to negotiate access. If you have difficulty, please contact researchdata@jcu.edu.au for assistance."
                         saveFile = True
                 ##Setting the citation Url for the child records.
                 if  ((jsonData["dc:identifier.rdf:PlainLiteral"] != "jcu.edu.au/collection/enmasse/1") and
                     (jsonData["dc:identifier.rdf:PlainLiteral"] != "jcu.edu.au/collection/enmasse/2") and
                     (jsonData["dc:identifier.rdf:PlainLiteral"] != "jcu.edu.au/collection/enmasse/3")):
                     if  "dc:biblioGraphicCitation.dc:hasPart.bibo:Website.dc:identifier" in jsonData:
                         print ("child: Found dc:biblio ") + jsonData["dc:biblioGraphicCitation.dc:hasPart.bibo:Website.dc:identifier"]
                         identifier = jsonData["dc:biblioGraphicCitation.dc:hasPart.bibo:Website.dc:identifier"]
                         identifier = identifier + "/data"
                         jsonData["dc:biblioGraphicCitation.dc:hasPart.bibo:Website.dc:identifier"] = identifier
                         saveFile = True
                     if  "bibo:Website.1.dc:identifier" in jsonData:
                         print ("child: Found bibo:Website ") + jsonData["bibo:Website.1.dc:identifier"]
                         identifier = jsonData["bibo:Website.1.dc:identifier"]
                         identifier = identifier + "/data"
                         jsonData["bibo:Website.1.dc:identifier"] = identifier
                         saveFile = True
                 ##Setting the citation Url for the parent records.
                 if  ((jsonData["dc:identifier.rdf:PlainLiteral"] == "jcu.edu.au/collection/enmasse/1") or
                     (jsonData["dc:identifier.rdf:PlainLiteral"] == "jcu.edu.au/collection/enmasse/2") or
                     (jsonData["dc:identifier.rdf:PlainLiteral"] == "jcu.edu.au/collection/enmasse/3")):
                     if  "dc:biblioGraphicCitation.dc:hasPart.bibo:Website.dc:identifier" in jsonData:
                         print ("parent: Found dc:biblio ") + jsonData["dc:biblioGraphicCitation.dc:hasPart.bibo:Website.dc:identifier"]
                         identifier = jsonData["dc:biblioGraphicCitation.dc:hasPart.bibo:Website.dc:identifier"]
                         identifier = "https://research.jcu.edu.au/enmasse/search/dataset/id_list=project_" + identifier[-1:]
                         jsonData["dc:biblioGraphicCitation.dc:hasPart.bibo:Website.dc:identifier"] = identifier
                         saveFile = True
                     if  "bibo:Website.1.dc:identifier" in jsonData:
                         print ("parent: Found bibo:Website ") + jsonData["bibo:Website.1.dc:identifier"]
                         identifier = jsonData["bibo:Website.1.dc:identifier"]
                         identifier = "https://research.jcu.edu.au/enmasse/search/dataset/id_list=project_" + identifier[-1:]
                         jsonData["bibo:Website.1.dc:identifier"] = identifier
                         saveFile = True

                 if  saveFile:
                     # magic happens here to make it pretty-printed
                     file = open(os.path.join(root, fileName), 'w')
                     file.write(json.dumps(jsonData, indent=4, sort_keys=True))
                     file.close()
                     print("Record processed: " + str(count) + " " + os.path.join(root, fileName))
            except ValueError as e:
                print ("Oops, there is a dodgy one: ", os.path.join(root, fileName)) 
                print ("ValueError: ", e)