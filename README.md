TDH-Research-Data-Catalogue
===========================

Maven
-----
Currently you need Maven 2.x to compile ReDBoX

Project Home
-----------

This repository contains the James Cook University RedBoX Institutional build.
After running mvn install on mint, ReDBoX, fascinator-shibboleth, and plugin-harvester-directoryName:

	#> mvn -Dproject.home=<deploy.directory> package

If you do not define project.home then it defaults to $HOME/deployment/redbox.

Deployment
==========

See [jcu-eresearch/TDH-Deployment](https://github.com/jcu-eresearch/TDH-Deployment) for our automatic deployment scripts.


System Setup
============
Once you have deployed the institutional build you will need to setup the init symlinks.

Redhat
------
    #> cd /etc/init.d
    #> ln -s <deploy.directory>/system/redhat/init redbox
    #> cd /etc/sysconfig
    #> ln -s <deploy.directory>/system/redhat/redbox redbox
    #> cd /var/log
    #> ln -s <deploy.directory>/home/logs redbox

Then edit /etc/sysconfig/redbox and set the `USER` variable.


Development
===========

During development it is often handy to have a profile in your settings.xml that 
redbox into your target directory, like such:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"
       	  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0 http://maven.apache.org/xsd/settings-1.0.0.xsd">
	.
	.
	.
	<profiles>
                <profile>
                    <id>deployment_location</id>
                    <properties>
                        <redbox.project.home>${project.build.directory}/deploy</redbox.project.home>
                    </properties>
                </profile>
                <profile>
                    <id>dev_hostname</id>
                    <properties>
                        <local.redbox.hostname>http://redbox.dev.hostname:${server.port}</local.redbox.hostname>
                    </properties>
                </profile>
	</profiles>
	.
	.
	.
</settings>
```
You just activate this profile in your IDE when you are working on it.
Alternatively, you can activate the profile with the `activeProfiles` section of ~/.m2/settings.xml
```xml
<?xml version="1.0" encoding="UTF-8"?>
<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"
       	  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0 http://maven.apache.org/xsd/settings-1.0.0.xsd">
	.
	.
	.
    <activeProfiles>
       	<activeProfile>deployment_location</activeProfile>
        <activeProfile>dev_hostname</activeProfile>
    </activeProfiles>
	.
	.
	.
</settings>
```

Credits
=======

This project is supported by the [Australian National Data Service (ANDS)](http://www.ands.org.au) through the National Collaborative Research Infrastructure Strategy Program and the Education Investment Fund (EIF) Super Science Initiative, as well as through the [Queensland Cyber Infrastructure Foundation (QCIF)](http://www.qcif.edu.au).

Licence
=======
This code is available under a GPL v2 licence - see [`LICENCE.txt`](./LICENCE.txt) for details.


