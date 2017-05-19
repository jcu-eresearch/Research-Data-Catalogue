import os
import json
import argparse

from os.path import join, getsize

##
# This data fix program is designed to clean up the 'curatedPid' in *.tfpackage due to a problem with the curation of Software Services.
# it should be showing jcu.edu.au/tdh/service/australian-birds

# This fix only needs to be executed once.
# 1. Check the queues in Mint and ReDBox. If they are empty, stop both servers. Back up the 'storage' folder in 'RedBox'
# 2. Restart Mint and ReDBox.
# 3. Run this script against redbox/storage folder.
# 4. Log into the ReDBox as admin, change to the 'Published' view, and 'reharvest' everything..wait, it takes a while.
#
 
parser = argparse.ArgumentParser(description='Perform data cleanup of Software Services')
parser.add_argument('storagePath', metavar='storagePath', help='The path of the storage folder within ReDBox.')

print 'Using the following path to process redbox cleanup: ', parser.parse_args().storagePath

count = 0

for root, dirs, files in os.walk(parser.parse_args().storagePath):
    for fileName in files:
         if (fileName == 'formData.tfpackage') or (fileName.endswith(".rif.tfpackage")):
            #print os.path.join(root, 'metadata.json')
            try:
                 file = open(os.path.join(root, fileName), 'r+')
                 jsonData = json.load(file)
                 file.close()
                 saveFile = False
                 if  "relationships" in jsonData:
                     for relationship in jsonData["relationships"]:
                         if  (relationship["identifier"] == "jcu.edu.au/tdh/service/australian-birds"):
                             relationship["curatedPid"] = "jcu.edu.au/tdh/service/australian-birds"
                             saveFile = True
                             count = count + 1
                             #print  ("Jay: fixed record ") + str(count) + " " + str(relationship)
                     if  saveFile:
                         # magic happens here to make it pretty-printed
                         file = open(os.path.join(root, fileName), 'w')
                         file.write(json.dumps(jsonData, indent=4, sort_keys=True))
                         file.close()
                         print("Record processed: " + str(count) + " " + os.path.join(root, fileName))
            except ValueError as e:
                print ("Oops, there is a dodgy one: ", os.path.join(root, fileName)) 
                print ("ValueError: ", e)