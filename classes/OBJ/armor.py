from const import *

class Armor():
    
    def __init__(self, type, level):
        self.type = type
        self.level = level
        self.imgNum = type + SHIELD
    
    def getType(self):
        return self.type
    def getLevel(self):
        return self.level
    def getImgNum(self):
        return self.imgNum