#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod


#*****************************************************
# Explorer
#*****************************************************
class Explorer(metaclass = ABCMeta):
    @abstractmethod
    def getContent(self, *args, **kwargs):
        pass

    @abstractmethod
    def getStlCategory(self):
        pass

    def getFreshContent(self, *args, **kwargs):
        pass

    def getStlCurDir(self):
        return ''

    def supportsMulti(self):
        return False

    def supportsNameOnly(self):
        return False

    def isFilePath(self):
        return True

