import re
import traceback
from com.googlecode.fascinator.api.storage import StorageException
from com.googlecode.fascinator.common import JsonSimple
from java.io import ByteArrayInputStream
from java.lang import Exception
from java.lang import String
from org.apache.commons.lang import StringEscapeUtils
from org.apache.commons.lang import StringUtils
from org.joda.time import DateTime, DateTimeZone

from java.util import TreeMap

class MigrateData:
    def __init__(self):
        self.packagePidSuffix = ".tfpackage"
        self.redboxVersion = None

    def __activate__(self, bindings):
        # Prepare variables
        self.systemConfig = bindings["systemConfig"]
        self.object = bindings["object"]
        self.log = bindings["log"]
        self.audit = bindings["auditMessages"]
        self.pidList = None

        # Look at some data
        self.oid = self.object.getId()

        try:
            # # check if object creation and modification dates...
            self.insertCreateAndModifiedDate()
            #
            # # load the package data..
            self.__getPackageData()
            if self.packageData is not None:
                self.log.info(self.packageData.toString(True))
                # update the redbox version...
                self.updateVersion()

                # # update description to wysiwyg descriptions and init for multiple descriptions
                self.setDescriptionShadow()

                # # check recordAsLocation config and, if true, set record as location
                self.setRecordAsLocation()

                # add access rights type if none exists, but relevant licence present
                self.updateRightsType()

                #update additional identifiers
                self.updateAdditionalIdentifier()

                # add new keys if not present
                self.injectFreshKeys()

                # # save the package data...
                self.__savePackageData()

            self.object.close()
        except Exception, e:
            traceback.print_exc()
            self.object = None

    def insertCreateAndModifiedDate(self):
        # check if object created and modified date exists, populate with current date if not..
        propMetadata = self.object.getMetadata()
        now = DateTime().toString()
        self.log.debug("date time now is: %s" % now)
        localTimeZoneHrs = str(DateTime().toString("ZZ"))
        self.log.info("current zone hours is: %s" % localTimeZoneHrs)
        createdDateTime = str(propMetadata.getProperty("date_object_created"))
        self.log.debug("created date time was: %s" % createdDateTime)
        if createdDateTime is None:
            self.log.debug("Updating created time...")
            propMetadata.setProperty("date_object_created", now)
        #elif createdDateTime.endswith("Z"):
            ## TODO : remove this temporary workaround to strip any UTC and replace with local timezone (for solr)
            #createdDateTimeAsLocal = re.sub("Z+$", "", createdDateTime) + localTimeZoneHrs
            #self.log.debug("updated created date time to: %s" % createdDateTimeAsLocal)
            #propMetadata.setProperty("date_object_created", createdDateTimeAsLocal)
        #else:
            #self.log.debug("existing created time does not end in 'Z', so remains untouched.")
        modifiedDateTime = str(propMetadata.getProperty("date_object_modified"))
        self.log.debug("modified date time was: %s" % modifiedDateTime)
        if modifiedDateTime is None:
            self.log.debug("Updating modified time...")
            propMetadata.setProperty("date_object_modified", now)
        #elif modifiedDateTime.endswith("Z"):
            ## TODO : remove this temporary workaround to strip any UTC and replace with local timezone (for solr)
            #modifiedDateTimeAsLocal = re.sub("Z+$", "", modifiedDateTime) + localTimeZoneHrs
            #self.log.debug("updated modified date time to: %s" % modifiedDateTimeAsLocal)
            #propMetadata.setProperty("date_object_modified", modifiedDateTimeAsLocal)
        #else:
            #self.log.debug("existing modified time does not end in 'Z', so remains untouched.")

    def updateVersion(self):
        if self.redboxVersion is None:
            self.redboxVersion = self.systemConfig.getString(None, ["redbox.version.string"])
        if self.redboxVersion is None:
            self.log.error("Error, could not determine system version!")
            return
        self.getPackageJson().put("redbox:formVersion", self.redboxVersion)

    # get a list of metadata using basekey. Used by repeatable elements like FOR code or people
    def getList(self, baseKey):

        if baseKey[-1:] != ".":
            baseKey = baseKey + "."
        valueMap = TreeMap()
        metadata = self.packageData.getJsonObject()

        for key in [k for k in metadata.keySet() if k.startswith(baseKey)]:
            value = metadata.get(key)
            field = key[len(baseKey):]
            index = field[:field.find(".")]

            if index == "":
                valueMapIndex = field[:key.rfind(".")]
                dataIndex = "value"
            else:
                valueMapIndex = index
                dataIndex = field[field.find(".")+1:]
            #self.log.info("%s. '%s'='%s' ('%s','%s')" % (index, key, value, valueMapIndex, dataIndex))
            data = valueMap.get(valueMapIndex)
            if not data:
                data = TreeMap()
                valueMap.put(valueMapIndex, data)
            data.put(dataIndex, value)

        return valueMap

    def formatDescription(self, description):
        unescapedDescription = ""
        escapedDescription = ""

        rawDescription = StringUtils.defaultString(description)

        if (rawDescription):
            # not completely accurate for checking for tags but ensures a style consistent with wysiwyg editor
            if re.search("^<p>.*</p>|^&lt;p&gt;.*&lt;\/p&gt;", rawDescription):
                ## deprecated description may be unescaped or escaped already - so ensure both cases covered
                unescapedDescription = StringEscapeUtils.unescapeHtml("%s" % rawDescription)
                escapedDescription = StringEscapeUtils.escapeHtml("%s" % rawDescription)
            else:
                unescapedDescription = StringEscapeUtils.unescapeHtml("<p>%s</p>" % rawDescription)
                escapedDescription = StringEscapeUtils.escapeHtml("<p>%s</p>" % rawDescription)

        return (unescapedDescription, escapedDescription)

    def setDescriptionShadow(self):
        deprecated_description = self.getPackageJson().get("dc:description")
        relevant_description = self.getPackageJson().get("dc:description.1.text")
        if self.getPackageJson().get("dc:description.0.text"):
            self.log.warn("Found current description for workflow initializer: 'dc:description.0.text'")
        if relevant_description:
            self.log.info(
                "Found current populated description for 'dc:description.1.text': %s, so skipping description migration..." % relevant_description)
            return
        else:
            unescapedDesc, escapedDesc= self.formatDescription(deprecated_description)
            self.log.info("relevant unescaped description is: %s" % unescapedDesc)
            self.log.info("relevant escaped description is: %s" % escapedDesc)

            deprecatedDescMatch = False

            descriptionList = self.getList('rif:description')

            idx = 1
            if  (descriptionList is not None and not descriptionList.isEmpty()):
                for description in descriptionList.keySet():
                    temp = descriptionList.get(description)
                    descType = temp.get('type')
                    descValue = temp.get('value')
                    descLabel = temp.get('label')

                    if  (deprecated_description ==  descValue):
                        deprecatedDescMatch = True

                    unescapedDescription, escapedDescription= self.formatDescription(descValue)
                    #adding new
                    self.log.info("Adding 'dc:description.x.' key: idx: " + str(idx) )
                    self.getPackageJson().put("dc:description."+str(idx)+".text", unescapedDescription)
                    self.getPackageJson().put("dc:description."+str(idx)+".shadow", escapedDescription)
                    self.getPackageJson().put("dc:description."+str(idx)+".type", descType)
                    #removing old
                    self.log.info("Removing 'rif:description.x.' key...")
                    self.getPackageJson().remove("rif:description."+str(idx)+".type")
                    self.getPackageJson().remove("rif:description."+str(idx)+".value")
                    self.getPackageJson().remove("rif:description."+str(idx)+".label")
                    idx += 1

            if  (deprecatedDescMatch == False):
                self.getPackageJson().put("dc:description."+str(idx)+".text", unescapedDesc)
                self.getPackageJson().put("dc:description."+str(idx)+".shadow", escapedDesc)
                self.getPackageJson().put("dc:description."+str(idx)+".type", "full")

            self.log.debug  ("Removing deprecated 'dc:description' key...")
            self.getPackageJson().remove("dc:description")
            self.log.debug(
                "Completed migrating 'dc:description' %s to dc:description.1.text|shadow" % deprecated_description)

    def updateAdditionalIdentifier(self):
        additionalIdList = self.getList('rif:collection')
        if  (additionalIdList is not None and not additionalIdList.isEmpty()):
            idx = 1
            for additionalId in additionalIdList.keySet():
                temp = additionalIdList.get(additionalId)
                identifier = temp.get('identifier')
                type = temp.get('type')
                label = temp.get('label')
                comment = temp.get('jcu:comment')

                #adding new
                self.log.debug("Adding 'dc:additionalidentifier.x.' key...")
                self.getPackageJson().put("dc:additionalidentifier."+str(idx)+".rdf:PlainLiteral", identifier)
                self.getPackageJson().put("dc:additionalidentifier."+str(idx)+".jcu:comment", comment)
                self.getPackageJson().put("dc:additionalidentifier."+str(idx)+".type.rdf:PlainLiteral", type)
                self.getPackageJson().put("dc:additionalidentifier."+str(idx)+".type.rdf.skos:prefLabel", label)

                #removing old
                self.log.debug("Removing 'rif:collection.x.' key...")
                self.getPackageJson().remove("rif:collection."+str(idx)+".type")
                self.getPackageJson().remove("rif:collection."+str(idx)+".label")
                self.getPackageJson().remove("rif:collection."+str(idx)+".jcu:comment")
                self.getPackageJson().remove("rif:collection."+str(idx)+".identifier")
                self.log.info("Completed migrating 'rif:collection' %s to dc:additionalidentifier" % identifier)
                idx += 1

    def setRecordAsLocation(self):
        hasRecordAsLocationDefault = self.systemConfig.getString("", "rifcs", "recordAsLocation", "default")
        if hasRecordAsLocationDefault:
            recordAsLocationTemplate = self.systemConfig.getString("", "rifcs", "recordAsLocation", "template")
            self.log.debug("record as location template is %s" % recordAsLocationTemplate)
            urlBase = self.systemConfig.getString("", "urlBase")
            self.log.debug("url base is: %s" % urlBase)
            urlBasePattern = "\$\{urlBase\}"
            oidBasePattern = "\$\{oid\}"
            recordAsLocation = re.sub(urlBasePattern, urlBase, recordAsLocationTemplate)
            recordAsLocation = re.sub(oidBasePattern, self.oid, recordAsLocation)
            self.log.info("record as location is: %s" % recordAsLocation)
            self.getPackageJson().put("recordAsLocationDefault", recordAsLocation)
        else:
            self.log.info("record as location default is: %s," % hasRecordAsLocationDefault,
                          "so skipping 'record as location' migration...")

    def updateRightsType(self):
        accessRightsType = self.getPackageJson().get("dc:accessRightsType")
        self.log.debug("access rights: %s" % accessRightsType)
        ## because a user can deliberately change access rights type to "", ensure only change for null access rights types
        if accessRightsType is None:
            license = StringUtils.defaultString(self.getPackageJson().get("dc:license.skos:prefLabel"))
            self.log.info("License rights is: %s " % license)
            if re.search("CC|ODC|PDDL", str(license), re.IGNORECASE):
                self.getPackageJson().put("dc:accessRightsType", "open")
                self.log.debug("Added access rights type.")
            else:
                self.getPackageJson().put("dc:accessRightsType", "")
                self.log.debug("Added empty access rights type, because licence is: %s" % license)
        else:
            self.log.info(
                "Record already has access rights type key, with value: %s, so skipping update rights type migration." % accessRightsType)

    def injectFreshKeys(self):
        for freshKey in ["identifierText.1.creatorName.input", "pcName.identifierText",
                         "identifierText.1.supName.input",
                         "identifierText.1.collaboratorName.input"]:
            if self.getPackageJson().get(freshKey) is None:
                self.getPackageJson().put(freshKey, "")
                self.log.debug("added fresh key: %s" % freshKey)
            else:
                self.log.info("skipping fresh key: %s as it already exists" % freshKey)

    def getPackageJson(self):
        return self.packageData.getJsonObject()

    def __getPackageData(self):
        # Find our package payload
        self.packagePid = None
        self.packageData = None
        try:
            self.pidList = self.object.getPayloadIdList()
            for pid in self.pidList:
                if pid.endswith(self.packagePidSuffix):
                    self.packagePid = pid
        except StorageException:
            self.log.error("Error accessing object PID list for object '{}' ", self.oid)
            return
        if self.packagePid is None:
            self.log.debug("Object '{}' has no package data", self.oid)
            return

        # Retrieve our package data

        try:
            payload = self.object.getPayload(self.packagePid)
            try:
                self.packageData = JsonSimple(payload.open())
            except Exception:
                self.log.error("Error parsing JSON '{}'", self.packagePid)
            finally:
                payload.close()
        except StorageException:
            self.log.error("Error accessing '{}'", self.packagePid)
            return

    def __savePackageData(self):
        jsonString = String(self.packageData.toString(True))
        inStream = ByteArrayInputStream(jsonString.getBytes("UTF-8"))
        try:
            self.object.updatePayload(self.packagePid, inStream)
        except StorageException, e:
            traceback.print_exc()
            self.log.error("Error updating package data payload: ", e)
