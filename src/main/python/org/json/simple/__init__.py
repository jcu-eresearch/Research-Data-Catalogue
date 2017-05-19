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

from pprint import pprint
import json
from StringIO import StringIO

class JsonSimple:
    def __init__(self, *args):#stream, obj=None):
        stream = None
        obj = None
        if len(args) == 0: obj = {}
        if len(args) == 1: stream = args[0]
        if len(args) == 2: stream,obj = args
        if stream is not None:
            if isinstance(stream, JsonObject):
                self.obj = stream.obj
            else:
                self.to_parse = stream
                self.obj = json.load(stream)
        if obj is not None:
            self.obj = obj


    def getObject(self, *args):
        ob = self.obj

        for i in args[0]:
            ob = ob[i]
        if isinstance(ob, dict):
            return JsonObject(None, ob)
        if isinstance(ob,list):
            return JSONArray(None, ob)
        return ob

    def put(self, key, val):
        self.obj[key] = val

    def keySet(self):
        return self.obj.keys()
    def get(self, key):
        return self.getObject([key])
    def __len__(self):
        return len(self.obj)

    def toString(self, val):
        a = StringIO()
        pprint(self.obj, a)
        return a.getvalue()

class Wrapper:
    def __init__(self, di):
        self.di = di
    def containsKey(self, key):
        return self.di.has_key(key)

class JsonObject(JsonSimple):
    def __getitem__(self, item):
        return Wrapper(self.obj[item])

class JSONArray(JsonSimple):
    def __iter__(self):
        return self.obj.__iter__()
