# Loop through the file dodgy.txt
# It contains a list of files that could not be fixed by dataCleanup-fixAndPreventMissingRecords.py.
# dodgy.txt is the file list output from the exception generated in the above script. Copy the rows and use them to create dodgy.txt
# These tfpackages contain newlines, which cause json editing to fail, newlines should not exist in json, but redbox doesn't care them.

#This script finds the existence of packageType and viewId by regex matching.
#packageType and viewId are deleted and a .bak of the original file is created.
# see "man sed" for further details

while read p; do
 sed -i '.bak' '/"packageType",/d; /"viewId",/d' $p
done < dodgy.txt

#while read p; do
# diff $p $p.bak
#done < dodgy.txt
