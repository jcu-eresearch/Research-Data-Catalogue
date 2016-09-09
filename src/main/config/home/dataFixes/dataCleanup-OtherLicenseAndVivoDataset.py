import os
import json
import argparse

from os.path import join, getsize

##
# Using restore.sh causes the script redboxMigration1.5.py to also run.
# The application of this script when running a restore is set in the 'system-config.json'
#
#The redboxMigration1.5.py script updates the redbox version but also moves the Licence fields to Other Licence and 
#sets these checkboxes to a value other than 'on'
#    dc:relation.vivo:Dataset.1.redbox:origin: external,
#    dc:relation.vivo:Dataset.1.redbox:publish: off,

#This dataCleanup script updates all tfpackages moving the License Other back to License and setting the checkbox values back to 'on'
#It applies a 'blanket' fix to this issue.

#redboxMigration1.5.py has been copied to redboxMigration1.6.1.py and modified to prevent this issue from occurring again.
#This is a JCU fix. Review for future upgrades.

# This fix only needs to be executed once.
# 1. Check the queues in Mint and ReDBox. If they are empty, stop both servers. Back up the 'storage' folder in 'RedBox'
# 2. Restart Mint and ReDBox.
# 3. Run this script against redbox/storage folder.
# 4. Log into the ReDBox as admin, change to the 'Published' view, and 'reharvest' everything..wait, it takes a while. :)
#
#Any records that are in error during this script need to be manually fixed. The error is due to newlines contained in the JSON. Python is not tolerant of this. 
 
parser = argparse.ArgumentParser(description='Perform data cleanup of Software Services')
parser.add_argument('storagePath', metavar='storagePath', help='The path of the storage folder within ReDBox.')

print 'Using the following path to process redbox cleanup: ', parser.parse_args().storagePath

count = 0
dodgyCount = 0

for root, dirs, files in os.walk(parser.parse_args().storagePath):
    for fileName in files:
         #Edgar ||  XML Import of old repo || EnMaSSe
         if ((fileName == 'formData.tfpackage') or fileName.endswith(".rif.tfpackage") or fileName.endswith("xml.1.tfpackage")):
            #print os.path.join(root, 'metadata.json')
            try:
                 file = open(os.path.join(root, fileName), 'r+')
                 jsonData = json.load(file)
                 file.close()
                 saveFile = False

                 ##Checking for the population of the 'License Other' fields.
                 if  (("dc:license.rdf:Alt.dc:identifier" in jsonData) and (jsonData["dc:license.rdf:Alt.dc:identifier"] != "") and 
                      ("dc:license.rdf:Alt.skos:prefLabel" in jsonData) and (jsonData["dc:license.rdf:Alt.skos:prefLabel"] != "")):

                     #Moving "License Other" back to "License"
                     jsonData["dc:license.dc:identifier"] = jsonData["dc:license.rdf:Alt.dc:identifier"]
                     del jsonData["dc:license.rdf:Alt.dc:identifier"]
                     jsonData["dc:license.skos:prefLabel"] = jsonData["dc:license.rdf:Alt.skos:prefLabel"]
                     del jsonData["dc:license.rdf:Alt.skos:prefLabel"]

                     #print ("Post:" + "**dc:license.dc:identifier:       **  " + str(jsonData["dc:license.dc:identifier"])  + " **dc:license.skos:prefLabel**:         " + str(jsonData["dc:license.skos:prefLabel"]) + "\n")
                     saveFile = True
                            
                 datasetCount = 1
                 redboxOriginField = "dc:relation.vivo:Dataset." + str(datasetCount) + ".redbox:origin"
                 redboxPublishField = "dc:relation.vivo:Dataset." + str(datasetCount) + ".redbox:publish"
                 #While the fields are populated ("dc:relation.vivo:Dataset.1.redbox:origin" and "dc:relation.vivo:Dataset.1.redbox:publish") 
                 while ((redboxOriginField in jsonData) and (jsonData[redboxOriginField] != "") and
                        (redboxPublishField in jsonData) and (jsonData[redboxPublishField] != "")):
                       #print ("Pre: " + "**" + redboxOriginField + "**: " + str(jsonData[redboxOriginField]) + " **" + redboxPublishField + "**: " + str(jsonData[redboxPublishField]))
                       
                       if  (jsonData[redboxOriginField] == "external"):
                           jsonData[redboxOriginField] = "on"
                           saveFile = True
                       if  (jsonData[redboxPublishField] == "off"):
                           jsonData[redboxPublishField] = "on"
                           saveFile = True
                       print ("Post:" + "**" + redboxOriginField + "**: " + str(jsonData[redboxOriginField]) + " **" + redboxPublishField + "**: " + str(jsonData[redboxPublishField]) + "\n\n")
                       datasetCount = datasetCount + 1
                       redboxOriginField = "dc:relation.vivo:Dataset." + str(datasetCount) + ".redbox:origin"
                       redboxPublishField = "dc:relation.vivo:Dataset." + str(datasetCount) + ".redbox:publish"

                 if  saveFile:
                     # magic happens here to make it pretty-printed
                     file = open(os.path.join(root, fileName), 'w')
                     file.write(json.dumps(jsonData, indent=4, sort_keys=True))
                     file.close()
                     count = count + 1
                     print("Record processed: " + str(count) + " " + os.path.join(root, fileName))
            except ValueError as e:
                dodgyCount = dodgyCount + 1
                print ("Oops, this one is dodgy: " + str(dodgyCount), os.path.join(root, fileName)) 
                print ("ValueError: ", e)
