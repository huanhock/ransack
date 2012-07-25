import os, pygame, pickle

from random import choice, randrange

#from IMG import images

dirDict = { 'w':(-1,0), 'e':(1,0), 'n':(0,-1), 's':(0,1) }
DefaultWallTile = 29

class Room():
    def __init__(self, xdim, ydim, pos=(0,0), shape='Square'):
        self.pos = pos
        self.xdim = xdim
        self.ydim = ydim
        self.grid = []
        self.entrances = []
        
        if shape == 'square':
            (xpos, ypos) = self.getPos()
            (xdim, ydim) = room.getDimensions()
            for i in range(xdim+1):
                self.setGrid(i+xpos, ypos, DefaultWallTile)
                self.setGrid(i+xpos, ypos+ydim, DefaultWallTile)
            for i in range(ydim+1):
                self.setGrid(xpos, i+ypos, DefaultWallTile)
                self.setGrid(xpos+xdim, i+ypos, DefaultWallTile)
            for i in range(1,xdim):
                for j in range(1,ydim):
                    self.setGrid(xpos+i, ypos+j, 0)
        
    def getDimensions(self):
        return (self.xdim, self.ydim)
    
    def getPos(self):
        return self.pos
    
    def setPos(self, pos):
        self.pos = pos
    
    def setGrid(self, x, y, e):
        pass
    
    def getGrid(self, x, y):
        pass

class Map():
    def __init__(self, DIM):
        self.grid = []
        for i in range(DIM):
            self.grid += [[126]*DIM]
        self.DIM = DIM
        
        self.chests = {}
    
    def rollDie(self, target, range):
        d = randrange(range)
        if target >= d:
            return True
        else:
            return False
    
    def setMapEntry(self, x, y, e):
        if 0 <= x < self.DIM and 0 <= y < self.DIM:
            self.grid[y] = self.grid[y][:x] + [e] + self.grid[y][x+1:]
    
    def getMapEntry(self, x, y):
        if 0 <= x < self.DIM and 0 <= y < self.DIM:
            return self.grid[y][x]
        else: return -1
    
    def genRoom(self, pos=(0,0) ):
        return Room( randrange(4,7), randrange(4,7), pos, shape='square' )
        
    def branchTile(self, room):
        (xpos, ypos) = room.getPos()
        (xdim, ydim) = room.getDimensions()
        candidateList = []
        for i in range(1,xdim-2):
            candidateList += [(i+xpos,ypos)] + [(i+xpos,ypos+ydim)]
        for j in range(1,ydim-2):
            candidateList += [(xpos,i+ypos)] + [(xpos+xdim,i+ypos)]
        cand = choice(candidateList)
        if cand[0] == xpos:
            return (cand, 'w')
        elif cand[0] == xpos+xdim:
            return (cand, 'e')
        elif cand[1] == ypos:
            return (cand, 'n')
        elif cand[1] == ypos+ydim:
            return (cand, 's')
    
    def checkNewRoom(self, newRoom, tile, dir):
        (xpos, ypos) = tile
        (xdim, ydim) = newRoom.getDimensions()
        if xpos + xdim + 1 >= self.DIM or ypos + ydim + 1 >= self.DIM:
            return False
        if xpos - xdim - 1 < 0 or ypos - ydim - 1 < 0:
            return False
        if dir == 'n':
            newRoomPos = ( xpos - xdim/2, (ypos - ydim) -1 )
        elif dir == 's':
            newRoomPos = ( xpos - xdim/2, ypos + 1 )
        elif dir == 'w':
            newRoomPos = ( (xpos - xdim)-1, ypos - ydim/2 )
        elif dir == 'e':
            newRoomPos = ( xpos + 1, ypos - ydim/2 )
        for i in range(newRoomPos[0], newRoomPos[0]+xdim):
            for j in range(newRoomPos[1], newRoomPos[1]+ydim):
                if self.getMapEntry(i, j) != 126:
                    return False
        newRoom.setPos(newRoomPos)
        return True
    
    def generateMap(self, maxRooms):
        rooms = []
        startingRoom = self.genRoom()
        (xdim, ydim) = startingRoom.getDimensions()
        startingRoom.setPos( ( (self.DIM/2)-(xdim/2), (self.DIM/2)-(ydim/2) ) )
        self.addRoom(startingRoom)
        rooms += [startingRoom]
        #self.draw()
        
        while len(rooms) < maxRooms:
        
            # 4 select random room
            
            candidateRoom = choice(rooms)
            
            # 5 select random wall tile from above room
            
            tile, dir = self.branchTile(candidateRoom)
            
            # 6 generate new room
            
            newRoom = self.genRoom()
            
            # 7 see if new room fits next to selected room
            if self.checkNewRoom(newRoom, tile, dir):
            # 8  if yes - continue, if not go back to step 4
            
            # 9 add new room to map and list of rooms
                self.addRoom(newRoom)
                rooms += [newRoom]
                
            #10 create doorway into new room
                (x1,y1) = tile
                self.setMapEntry( x1,y1,0 )
                candidateRoom.entrances.append( (x1,y1) )
                (x2,y2) = dirDict[dir]
                self.setMapEntry( x1+x2, y1+y2, 0)
                newRoom.entrances.append( (x1+x2,y1+y2) )
            # 11 repeat step 4
            #self.draw()
        # set staircases
        # up
        choice1 = choice(rooms)
        (xpos, ypos) = choice1.getPos()
        (xdim, ydim) = choice1.getDimensions()
        self.setMapEntry( xpos + xdim/2, ypos + ydim/2, 120)
        self.POE = ( xpos + xdim/2, ypos + ydim/2 )
        rooms.remove(choice1)
        # down
        choice2 = choice(rooms)
        # find room with only 1 entrance
        # WARNING: this algorithm not guaranteed to stop.
        while len(choice2.entrances) > 1:
            choice2 = choice(rooms)
        (xpos, ypos) = choice2.getPos()
        (xdim, ydim) = choice2.getDimensions()
        (doorX, doorY) = choice2.entrances[0]
        self.setMapEntry( xpos + xdim/2, ypos + ydim/2, 121)
        self.setMapEntry( doorX, doorY, 116)
        self.POEx = ( xpos + xdim/2, ypos + ydim/2 )
        rooms.remove(choice2)
        
        # add key for door
        keyRoom = choice(rooms)
        (xpos, ypos) = keyRoom.getPos()
        (xdim, ydim) = keyRoom.getDimensions()
        self.setMapEntry( xpos + xdim/2, ypos + ydim/2, 98)
        rooms.remove(keyRoom)
        
        # set hero starting location - optional
        choice3 = choice(rooms)
        (xpos, ypos) = choice3.getPos()
        (xdim, ydim) = choice3.getDimensions()
        self.hs = ( xpos + xdim/2, ypos + ydim/2 )
        rooms.remove(choice3)
        
        #add chests
        chestlist = []
        for i in range(maxRooms/10):
            choice4 = choice(rooms)
            (xpos, ypos) = choice4.getPos()
            (xdim, ydim) = choice4.getDimensions()
            chestItems = []
            if self.rollDie(0,2) and self.rollDie(0,2):
                chestItems = [(6,1),(9,1)]
            elif self.rollDie(0,2):
                chestItems.append((0,1))
            else: chestItems.append((4,1))
            self.setMapEntry( xpos + xdim/2, ypos + ydim/2, 110)
            chestlist += [( ( xpos + xdim/2, ypos + ydim/2), chestItems )]
            rooms.remove(choice4)
        self.chests = dict(chestlist)
        
        #self.draw()
    
    def getMapBall(self):
        return (self.grid, self.POE, self.POEx, self.POE, self.chests )
    
    def saveMap(self):
        #filename = self.getFilename()
        ball = self.getMapBall()
        try:
            save = open('rmap.dat', "w")
            pickle.dump(ball, save)
            save.close()
        except pygame.error, message:
            print 'Cannot save map:', name
            raise SystemExit, message
    
    def mapCut(self, x, y):
        pass
    
    def mapCopy(self, x, y):
        pass
    
    def mapPaste(self, pos):
        pass
    
    def draw(self):
        gridField.fill( [0,0,0] )
        for i in range(DIM):
            for j in range(DIM):
                gridField.blit( images.mapImages[myMap.getMapEntry(i,j)], (i*blocksize,j*blocksize) )

        screen.blit(gridField, (0,0) )
        pygame.display.flip()
        while (pygame.event.wait().type != pygame.KEYDOWN): pass