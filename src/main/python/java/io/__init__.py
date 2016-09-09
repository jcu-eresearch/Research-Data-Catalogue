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

class FileInputStream:
    def __init__(self, _file):
        self.file = _file
        self.file.open()

    def close(self):
        self.file.close()

    def read(self, *args):
        return  self.file.read(*args)


class InputStreamReader:
    def __init__(self, stream, encoding):
        self.stream = stream
        self.encoding = encoding

    def read(self, *args):
        return self.stream.read(*args).encode(self.encoding)

    def close(self):
        self.stream.close()

class File:
    def __init__(self, path):
        self.path = path
    def open(self):
        self.f = open(self.path)

    def read(self, *args):
        return self.f.read(*args)

    def close(self):
        self.f.close()

class PrintWriter:
    def println(self, message):
        print message
    def close(self): pass