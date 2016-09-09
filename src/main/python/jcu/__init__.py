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

from java.io import PrintWriter

class log:
    def error(self, *args):
        a = args[0]
        b = args[1:]
        print "[ERROR]", a.format(*b)

    def info(self, *args):
        a = args[0]
        b = args[1:]
        print "[INFO ]", a.format(*b)

    def debug(self, *args):
        a = args[0]
        b = args[1:]
        print "[DEBUG]", a.format(*b)

class response:
    def setStatus(self, status): pass

    def getPrintWriter(self, mime): return PrintWriter()

class config:
    def __init__(self, home, data):
        self.data = data
        self.home = home
    def getString(self, *args):
        print args
        if args[1] == 'redbox.version.string':
            return "1.5.2.2"
        d = self.data
        for i in args[1]:
            d = d[i]
        if d is None:
            return None
        return d.replace("${fascinator.home}",self.home)


class config_helper:

    def __init__(self, config):
        self.config = config

    def __setattr__(self, key, value):
        if key == "config":
            self.__dict__[key] = value
        else:
            self.config[key] = value

    def __getitem__(self, item):
        return self.config[item]

    def __setitem__(self, key, item):
        self.config[key] = item

    def __getattr__(self, key):
        if key is "__str__": return self.config.__str__
        elif key is "__repr__": return self.config.__repr__
        elif key is "__iter__": return self.config.__iter__
        elif key is "config_delegate": return self.config
        return self.config[key]

    def __contains__(self, item):
        return self.__getattr__(item)