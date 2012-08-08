from const import *

from SCRIPTS import armorScr

class Armor():
    
    def __init__(self, type, level):
        self.type = type
        self.level = level
        self.imgNum = type + FRUIT1
        self.name = 'armor'
        self.desc = armorScr.descDict[self.type]
    
    def getType(self):
        return self.type
    def getLevel(self):
        return self.level
    def getImg(self):
        return self.imgNum
    def getName(self):
        return self.name
    def getDesc(self):
        return self.desc