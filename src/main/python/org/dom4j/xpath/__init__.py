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

class DefaultNamespaceContext: pass

class NodeWrapper:
    def __init__(self, node):
        if isinstance(node, NodeWrapper):
            self.node = node.node
        else:
            self.node = node

    def getValue(self):
        if self.node.__class__.__dict__.has_key('text'):
            return self.node.text.encode("utf-8")
        return self.node

    def xpath(self, p, namespaces={}):
        return fix(self.node.xpath(p, namespaces=namespaces))

def fix(nodes):
    return [NodeWrapper(x) for x in nodes]

class DefaultXPath:
    def __init__(self, xpath):
        self.xpath = xpath
    def setNamespaceContext(self, namespace):
        self.namespace = namespace

    def selectNodes(self, root):
        p = self.xpath
        return fix(root.xpath(p, namespaces={"rif": "http://ands.org.au/standards/rif-cs/registryObjects"}))

