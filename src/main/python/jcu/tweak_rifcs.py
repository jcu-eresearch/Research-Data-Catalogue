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

from lxml import etree as ET

import requests
import json, urllib
import os.path, re
from jcu import config_helper
from datetime import datetime
from StringIO import StringIO

def getConfig(args):
    mint_solr_url = "{mint_protocol}://{mint_host}:{mint_port}/solr/fascinator".format(**(args.__dict__))
    mint_url = "{mint_protocol}://{mint_host}:{mint_port}/{redbox_context}".format(**(args.__dict__))
    redbox_url = "{redbox_protocol}://{redbox_host}:{redbox_port}/{redbox_context}".format(**(args.__dict__))
    return config_helper({
        "mint_url":mint_url,
        "mint_solr_url": mint_solr_url,
        "redbox_url":redbox_url,
        "anzsrc_query": '{mint_solr_url}/select?wt=json&q=dc_identifier%%3D"{query}"'.format(mint_solr_url=mint_solr_url, query="%s"),
        "dc_i_query": '{mint_solr_url}/select?wt=json&q=dc_identifier%%3D"{query}"'.format(mint_solr_url=mint_solr_url, query="%s"),
        "user_query": '{mint_solr_url}/select?wt=json&q=known_ids%%3D"{query}"'.format(mint_solr_url=mint_solr_url, query="%s"),
        "field_query": '{mint_solr_url}/select?wt=json&q={field}%3A{value}',
        "license_url": "{redbox_url}/default/workflows/forms/data/licences.json".format(redbox_url=redbox_url)
    })


namespace = {"rif": "http://ands.org.au/standards/rif-cs/registryObjects"}

def solrFieldQuery(field, value, config):
    return config.field_query.format(mint_solr_url=config.mint_solr_url, field=field, value=urllib.quote(value, safe=''))


def fix(path, args, output):
    config = getConfig(args)
    config.licenses = json.loads(requests.get(config.license_url).text)
    name = os.path.split(path)[1]

    tree = ET.parse(path)

    if name.startswith("party_"):
        #fix_party(tree, config)
        return
    elif name.startswith("collection_"):
        fix_collection(tree, config)
    elif name.startswith("activity_"):
        fix_activity(tree, config)
    else:
        raise Exception("Unknown Type")

    out_path = path
    if output:
        out_path = os.path.join(output, name)
    tree.write(out_path, encoding='utf-8')


def fix_party(tree, config): pass


def fix_activity(tree, config): pass



def fix_descriptions(description, config):
    for des in description:
        des.attrib['label'] = "%s:"%des.attrib['type'].capitalize()

def fix_extent(related, config):
    ex = ET.SubElement(related[0], "DATA_MANAGEMENT")
    ex.attrib['size'] = "0"
    ex.attrib['period'] = "0"

def fix_collections(collections, config):
    for collection in collections:
#        collection.attrib['dateAccessioned'] = collection.attrib['dateAccessioned'].split("T")[0]
#        collection.attrib['dateModified'] =  collection.attrib['dateModified'].split("T")[0]
        now = datetime.now()
        collection.attrib['dateAccessioned'] = "%s-%s-%s"%(now.year, now.month, now.day)
        collection.attrib['dateModified'] =  "%s-%s-%s"%(now.year, now.month, now.day)

def fix_key(keys, config):
    for key in keys:
        if key.text.strip().startswith("jcu.edu.au/tdh/collection/"):
            key.text = key.text.strip()
            key.attrib['type'] = "local"
            key.attrib['origin']="external"
            key.attrib['label']="Local Identifier"


email_remap = {
    "jjvanderwal@gmail.com":"jeremy.vanderwal@jcu.edu.au",
}

def fix_emails(emails, config):
    for email in emails:
        fix_email(email, config)

def fix_email(email, config):
    value = email.xpath("rif:value", namespaces=namespace)[0]
    eml = value.text.strip()
    eml = eml.replace("Email: ", "")
    eml = eml.replace("email: ", "")
    eml = eml.replace("e-mail: ", "")
    eml = eml.lower()
    if eml in email_remap:
        eml = email_remap[eml]
    value.text = eml
    r = requests.get(solrFieldQuery("Email", eml, config))
    solrResponse = json.loads(r.text)
    if solrResponse['response']['numFound'] > 1:
        raise Exception("More than one email address: " + eml)
    if len(solrResponse['response']['docs']) > 0:
        entry = solrResponse['response']['docs'][0]
        email.attrib['hon'] = entry['Honorific'][0]
        email.attrib['givenName'] = entry['Given_Name'][0]
        email.attrib['familyName'] = entry['Family_Name'][0]
    else:
        print "Cannot find email address: ", eml



def fix_land_addresss(addressess, config):
    for addr in addressess:
        fix_land_address(addr, config)

def fix_land_address(addresses, config):
    ad = addresses.xpath("rif:addressPart[@type='addressLine']", namespaces=namespace)
    address = "\n".join([i.text.strip() for i in ad]).strip()
    map(lambda a: addresses.remove(a), ad)
    el = ET.SubElement(addresses, "addressPart")
    el.attrib['type'] = "combined"
    el.text = address

uri_types = {}

def fix_relatedInfos(rels, config):
    for rel in rels:
        fix_relatedInfo(rel, config)

def fix_relatedInfo(rel, config):
    licenses = {}
    for lic in config.licenses['results']:
        licenses[lic['id']] = lic['label']
        if not uri_types.has_key(lic['id']):
            uri_types[lic['id']] = "license"

    uri_keys = uri_types.keys()
    id = rel.xpath("rif:identifier", namespaces=namespace)[0]
    _notes = rel.xpath("rif:notes", namespaces=namespace)
    notes = None
    if len(_notes) > 0: notes = _notes[0]
    id.attrib['uritype'] = 'url'
    val = id.text.strip()
    if id.attrib.has_key('type'):
        if id.attrib['type'] == 'uri':
            for ukey in uri_keys:
                if val.startswith(ukey):
                    id.attrib['uritype'] = uri_types[ukey]
                    id.text = ukey
                    notes.text = licenses[ukey]
                    break


def fix_relatedObjects(related, config):
    for rel in related:
        fix_relatedObject(rel, config)

def fix_relatedObject(rel, config):
    relation_nodes = rel.xpath("rif:key", namespaces=namespace)
    for key_node in relation_nodes:
        key = key_node.text.strip()
        if key.startswith("jcu.edu.au/tdh/party/"):
            fix_relatedObject_Party(rel, config)
        elif key.startswith("jcu.edu.au/tdh/activity/"):
            fix_relatedObject_Activity(rel, config)
        else:
            raise Exception("Unknown Related Object Type")


def fix_relatedObject_Activity(rel, config):
    id_node = rel.xpath("rif:key", namespaces=namespace)[0]
    id_node.text = id_node.text.strip().replace("jcu.edu.au/tdh/activity/", "jcu.edu.au/activity/")
    r = requests.get(solrFieldQuery("dc_identifier", id_node.text, config))
    solrResponse = json.loads(r.text)
    if solrResponse['response']['numFound'] == 1:
        entry = solrResponse['response']['docs'][0]
        rel.attrib['title'] = entry['dc_title']
        rel.attrib['grantNumber'] = id_node.text.replace("jcu.edu.au/activity/", "")
#        print id_node.text.replace("jcu.edu.au/activity/", "")


def fix_relatedObject_Party(rel, config):
    id_node = rel.xpath("rif:key", namespaces=namespace)
    relation_node = rel.xpath("rif:relation", namespaces=namespace)
    id = id_node[0].text.strip()
    r = requests.get(config.user_query % id)
    solrResponse = json.loads(r.text)

    if solrResponse['response']['numFound'] != 1:
        return
    entry = solrResponse['response']['docs'][0]
    id_node[0].text = entry['dc_identifier'][0]
    fields = ["Family_Name", "Given_Name", "Honorific", "dc_title", "primary_group_id"]
    for fld in fields:
        if  isinstance(entry[fld], list):
            if len(entry[fld]) > 1:
                raise Exception("Only one element expected for: %s, got %s" % (fld, len(entry[fld])))
            rel.attrib[fld] = entry[fld][0]
        else:
            rel.attrib[fld] = entry[fld]
    id_node[0].text = entry["dc_identifier"][0]

    labels = {
        "hasAssociationWith": "Associated with:",
        "hasCollector": "Aggregated by:",
        "isEnrichedBy": "Enriched by:",
        "isManagedBy": "Managed by:",
        "isOwnedBy": "Owned by:",
        }

    relation_node[0].attrib['label'] = labels[relation_node[0].attrib['type']]

    r = requests.get(solrFieldQuery("dc_identifier", entry["primary_group_id"][0], config))
    orgu_res = json.loads(r.text.encode("utf-8"))
    rel.attrib["primary_group_name"] = orgu_res['response']['docs'][0]["Name"][0]


def getTitle(id, orig, config):
    r = requests.get(config.anzsrc_query % id)
    solrResponse = json.loads(r.text)
    for val in solrResponse['response']['docs']:
        if id in val['dc_identifier']:
            return "%s - %s (%s)" % (orig, val['dc_title'], orig)

def add_australia(kmls, config):
    for kml in kmls:
        if len(kml.xpath("../rif:spatial[@type='text' and text()='Continental Australia']", namespaces=namespace)) == 0:
            australia = ET.SubElement(kml.getparent(), "spatial")
            australia.attrib['type']='text'
            australia.text="Continental Australia"
            return


def add_language(nodes, config):
    for node in nodes:
        lang = ET.SubElement(node, "LANGUAGE")
        lang.text="English"

def add_retention(nodes, config):
    for node in nodes:
        ret = ET.SubElement(node, "RETENTION")
        ret.text = "indefinitely"


def process_registryObject(nodes, config):
    add_language(nodes, config)
    add_retention(nodes, config)


def fix_kml(kmls, config):
    for kml in kmls:

        coords = re.findall(r"[\.\-+0-9]+", kml.text)
        _del = ""
        s = StringIO()
        s.write("POLYGON((")
        for i in range(0, len(coords), 2):
            s.write(_del)
            s.write(" ".join(coords[i:i+2]))
            _del = ", "
        s.write("))")
        kml.attrib['type']="text"
        wtk = ET.SubElement(kml, "wtk")
        wtk.text=s.getvalue()
        kml.text = s.getvalue()

collection_fixes = {
    "/rif:registryObjects/rif:registryObject/rif:key": fix_key,
    "/rif:registryObjects/rif:registryObject/rif:collection": fix_collections,
    "/rif:registryObjects/rif:registryObject/rif:collection/rif:relatedObject": fix_relatedObjects,
    "/rif:registryObjects/rif:registryObject/rif:collection/rif:location/rif:address/rif:electronic[@type='email']": fix_emails,
    "/rif:registryObjects/rif:registryObject/rif:collection/rif:location/rif:address/rif:physical[@type='streetAddress']": fix_land_addresss,
    "/rif:registryObjects/rif:registryObject/rif:collection/rif:description": fix_descriptions,
    #    "/rif:registryObjects/rif:registryObject": fix_extent,
    "/rif:registryObjects/rif:registryObject": process_registryObject,
    "/rif:registryObjects/rif:registryObject/rif:collection/rif:relatedInfo":fix_relatedInfos,
    "/rif:registryObjects/rif:registryObject/rif:collection/rif:coverage/rif:spatial[@type='kmlPolyCoords']": fix_kml,
#    "/rif:registryObjects/rif:registryObject/rif:collection/rif:coverage/rif:spatial":add_australia

}

def fix_collection(tree, config):
    subjects = tree.xpath("/rif:registryObjects/rif:registryObject/rif:collection/rif:subject", namespaces=namespace)
    for subject in subjects:
        if subject.attrib.has_key("type"):
            if subject.attrib['type'] == 'anzsrc-for':
                orig = subject.text.strip()
                subject.text = "http://purl.org/asc/1297.0/2008/for/" + orig
                subject.attrib['title'] = getTitle(subject.text, orig, config)
            if subject.attrib['type'] == 'anzsrc-seo':
                orig = subject.text.strip()
                subject.text = "http://purl.org/asc/1297.0/2008/seo/" + orig
                subject.attrib['title'] = getTitle(subject.text, orig, config)

    for fix in collection_fixes:
        tofix = tree.xpath(fix, namespaces=namespace)
        collection_fixes[fix](tofix, config)


    #    keys = tree.xpath("/rif:registryObjects/rif:registryObject/rif:key", namespaces=namespace)
    #    fix_key(keys, config)

    #    collections = tree.xpath("/rif:registryObjects/rif:registryObject/rif:collection", namespaces=namespace)
    #    fix_collections(collections, config)

    #    related = tree.xpath("/rif:registryObjects/rif:registryObject/rif:collection/rif:relatedObject",
    #        namespaces=namespace)
    #    for rel in related:
    #        fix_relatedObject(rel, config)

    #    emails = "/rif:registryObjects/rif:registryObject/rif:collection/rif:location/rif:address/rif:electronic[@type='email']"
    #    for email in tree.xpath(emails, namespaces=namespace):
    #        fix_email(email, config)

    #    addr = "/rif:registryObjects/rif:registryObject/rif:collection/rif:location/rif:address/rif:physical[@type='streetAddress']"
    #    for addresses in tree.xpath(addr, namespaces=namespace):
    #        fix_land_address(addresses, config)

    #    descriptions = "/rif:registryObjects/rif:registryObject/rif:collection/rif:description"
    #    fix_descriptions(tree.xpath(descriptions, namespaces=namespace), config)

    ##    related = tree.xpath("/rif:registryObjects/rif:registryObject", namespaces=namespace)
    ##    fix_extent(related, config)

    #    relatedInfo = tree.xpath("/rif:registryObjects/rif:registryObject/rif:collection/rif:relatedInfo",
    #        namespaces=namespace)
    #    fix_relatedInfos()
    #    for rl in relatedInfo:
    #        fix_relatedInfo(rl, config)