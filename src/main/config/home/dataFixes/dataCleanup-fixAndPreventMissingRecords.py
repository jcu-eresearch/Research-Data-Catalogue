import os
import json
import argparse

from os.path import join, getsize

##
# Editing older published records causes them to disappear.
# in the *.tfpackage, metalist contains a list of fields. In older records metalist contains packageType and viewId.
# When packageType and viewId exist with values, but the field name is also in the metaList the field and values get deleted.
# When a query is run to display/list records, they are not found, as they must have packageType:dataset

#To prevent this problem going forward, packageType and viewId are to be removed from the metalist.

#To fix already missing records, add fields:
#  viewId : "default"
#  packageType : "dataset"

#This script will generate some exceptions printing out the file path.
#These tfpackages contain newlines, which are not compativle with json, especially in python. Redbox processing doesn't care about them.
#The script fixRecords.sh has been build to apply the sames changes, but using bash. Please refer to it to complete the cleanup.

#Once applied this cleanup should not be required again.

parser = argparse.ArgumentParser(description='Perform data cleanup of Software Services')
parser.add_argument('storagePath', metavar='storagePath', help='The path of the storage folder within ReDBox.')

print 'Using the following path to process redbox cleanup: ', parser.parse_args().storagePath

count = 0
dodgyCount = 0

for root, dirs, files in os.walk(parser.parse_args().storagePath):
    for fileName in files:
         if fileName.endswith(".tfpackage"):
            #print os.path.join(root, 'metadata.json')
            try:
                 file = open(os.path.join(root, fileName), 'r+')
                 jsonData = json.load(file)
                 file.close()
                 saveFile = False

                 count = count + 1

                 if  ("metaList" in jsonData):

                     ##Identify records that are OK, used for testing purposes
                     #if  (("viewId" not in jsonData["metaList"]) and ("packageType" not in jsonData["metaList"]) and
                     #         ("viewId" in jsonData) and ("packageType" in jsonData)):
                         #print("OK: " + os.path.join(root, fileName))

                     ##Another test, records where viewid and packageType are in metaList, but not the fields. There shouldn't be any in this scenario.
                     #if  (("viewId" in jsonData["metaList"]) and ("packageType" in jsonData["metaList"]) and
                     #         ("viewId" not in jsonData) and ("packageType" not in jsonData)):
                         #print("Should not exist: " + os.path.join(root, fileName))

                     #Identify records where viewId and packageType are in *.tfpackage and metaList
                     if  (("viewId" in jsonData["metaList"]) and ("packageType" in jsonData["metaList"]) and
                          ("viewId" in jsonData) and ("packageType" in jsonData)):
                         jsonData["metaList"].remove("viewId")
                         jsonData["metaList"].remove("packageType")
                         #print("Fixed: " + os.path.join(root, fileName))
                         saveFile = True

                     ##Records where viewId and packageType do not exist, i.e. fix ones that have become lost.
                     if  (("viewId" not in jsonData) and ("packageType" not in jsonData)):
                        jsonData["packageType"] = "dataset"
                        jsonData["viewId"] = "default"
                        #print("Repaired: " + os.path.join(root, fileName))
                        saveFile = True

                     if  saveFile:
                         # magic happens here to make it pretty-printed
                         file = open(os.path.join(root, fileName), 'w')
                         file.write(json.dumps(jsonData, indent=4, sort_keys=True))
                         file.close()
                         #print("Record processed: " + str(count) + " " + os.path.join(root, fileName))
            except ValueError as e:
                dodgyCount = dodgyCount + 1
                #print ("Oops, this one is dodgy: " + str(dodgyCount), os.path.join(root, fileName))
                print (os.path.join(root, fileName))
                #print ("ValueError: ", e)

print ("Total count :" + str(count))