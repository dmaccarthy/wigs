# Copyright 2015-2016 D.G. MacCarthy <devwigs@gmail.com>
#
# This file is part of WIGS.
#
# WIGS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# WIGS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with WIGS.  If not, see <http://www.gnu.org/licenses/>.


from os.path import isfile
from shutil import copyfile, move, rmtree
import os

class FileSeq:

    def __init__(self, pattern, start=1, length=True, reverse=False):
        self.change = 1
        self.pattern = pattern
        self.start = start
        self._len = self.currentLength() if length is True else length 
        if reverse:
            self.start += self._len - 1
            self.change = -1

    def __getitem__(self, n):
        if n < 0: n += len(self)
        name = self._name(n)
        if self._len is not False and (n >= len(self) or n < 0):
            print(n)
            raise IndexError(name)
        return name

    def _name(self, n):
        i = self.start + n * self.change
        return self.pattern.format(i)

    def __len__(self):
        if self._len is False:
            raise Exception("sequence is infinite")
        return self._len

    def currentLength(self):
        if isfile(self._name(0)): i0 = 0
        else: return 0
        n = 256
        while isfile(self._name(i0+n)):
            i0 += n
            n *= 2
        i1 = i0 + n
        while True:
            if i0 == i1: return i0 + 1
            elif i1 - i0 == 1:
                n = i1 if isfile(self._name(i1)) else i0
                return n + 1
            n = (i0 + i1) // 2
            if isfile(self._name(n)): i0 = n
            else: i1 = n

    def apply(self, fs, func):
        if type(fs) is str:
            fs = FileSeq(fs, length=False)
        i = 0
        for f in self:
            func(f, fs[i])
            i += 1

    def move(self, dest): self.apply(dest, move)
    def copy(self, dest): self.apply(dest, copyfile)

# Clipboard is experimental!

    fldr = "fs_clip"
    _clip = 0

    @property
    def clip(self):
        return self.fldr + "/cut{}.tmp"
    
    def resetClip(self):
        try: rmtree(self.fldr)
        except: pass
        os.mkdir(self.fldr)
        self._clip = 0
        
    def cut(self, start, n=1, shift=True):
        size = len(self)
        assert start + n <= size, "Invalid argument"
        self.resetClip()
        i = 0
        dest = self.clip
        while i < n:
            move(self[start + i], dest.format(i))
            i += 1
        if shift:
            start += n
            for i in range(size - start):
                move(self._name(start+i), self._name(start+i-n))
        self._clip = n
        self._len -= n

    def copyClip(self, i, n):
        self.resetClip()
        dest = self.clip
        for j in range(n):
            copyfile(self[i], dest.format(j))
            i += 1
        self._clip = n

    def paste(self, posn=None):
        i = len(self) - 1
        if posn is None: posn = i + 1
        fn = self.pattern
        while i >= posn:
            move(fn.format(i), fn.format(i+self._clip))
            i -= 1
        dest = self.clip
        for i in range(self._clip):
            move(dest.format(i), fn.format(i+posn))
            i += 1
        self._clip = 0