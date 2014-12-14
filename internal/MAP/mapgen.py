import os
import pygame
import pickle

from random import choice, randrange
from MAP import generalmap, tile, room
from UTIL import const, colors

from SCRIPTS import mEnemyScr, mapScr

#from IMG import images

dirDict = {'w': (-1, 0), 'e': (1, 0), 'n': (0, -1), 's': (0, 1)}
DefaultWallTile = 29

DEFAULTBKGD = 0


class Generator():

    def __init__(self, DIM, level=1):
        self.map = map.genMap(DIM, level)
        self.copyText = []
        self.level = level

    def rollDie(self, target, range):
        d = randrange(range)
        if target >= d:
            return True
        else:
            return False

    def genRoom(self, pos=(0, 0), shape='square'):
        return room.Room(randrange(5, 8), randrange(5, 8), pos, shape)

    # find a random exterior wall tile, see which way we're going
    def branchTile(self, map, room):
        (xpos, ypos) = room.getPos()
        (xdim, ydim) = room.getDimensions()
        candidateList = []
        for i in range(1, xdim - 1):
            if map.getEntry(i + xpos, ypos) == const.EWWALL:
                candidateList += [(i + xpos, ypos)] + [(
                                   i + xpos, ypos + ydim - 1)]
        for i in range(1, ydim - 1):
            if map.getEntry(xpos, i + ypos) == const.NSWALL:
                candidateList += [(xpos, i + ypos)] + [(
                                   xpos + xdim - 1, i + ypos)]
        cand = choice(candidateList)
        if cand[0] == xpos:
            return (cand, 'w')
        elif cand[0] == xpos + xdim - 1:
            return (cand, 'e')
        elif cand[1] == ypos:
            return (cand, 'n')
        elif cand[1] == ypos + ydim - 1:
            return (cand, 's')

    def checkNewRoom(self, map, newRoom, tile, dir):
        (xpos, ypos) = tile
        (xdim, ydim) = newRoom.getDimensions()
        if xpos + xdim + 1 >= map.DIM or ypos + ydim + 1 >= map.DIM:
            return False
        if xpos - xdim - 1 < 0 or ypos - ydim - 1 < 0:
            return False
        if dir == 'n':
            newRoomPos = (xpos - xdim / 2, (ypos - ydim))
        elif dir == 's':
            newRoomPos = (xpos - xdim / 2, ypos + 1)
        elif dir == 'w':
            newRoomPos = ((xpos - xdim), ypos - ydim / 2)
        elif dir == 'e':
            newRoomPos = (xpos + 1, ypos - ydim / 2)
        for i in range(newRoomPos[0], newRoomPos[0] + xdim):
            for j in range(newRoomPos[1], newRoomPos[1] + ydim):
                if map.getEntry(i, j) != const.VOID:
                    return False
        newRoom.setPos(newRoomPos)
        return True

    def generateMap(self, maxRooms):
        rooms = []
        startingRoom = self.genRoom((0, 0), 'round')
        (xdim, ydim) = startingRoom.getDimensions()
        startingRoom.setPos(((self.map.DIM / 2) - (xdim / 2),
            (self.map.DIM / 2) - (ydim / 2)))
        self.addRoom(self.map, startingRoom, startingRoom.getPos())
        rooms += [startingRoom]
        self.secretRooms = []

        while len(rooms) < maxRooms:

            # 4 select random room
            candidateRoom = choice(rooms)

            # 5 select random wall tile from above room
            tile, dir = self.branchTile(self.map, candidateRoom)

            # 6 generate new room
            '''
            if len(rooms) in [5,10,15]:
                newRoom = self.genRoom((0,0), 'round')
            else: newRoom = self.genRoom()
            '''
            newRoom = self.genRoom()

            # 7 see if new room fits next to selected room
            if self.checkNewRoom(self.map, newRoom, tile, dir):
                startingRoom.setPos(((self.map.DIM / 2) - (xdim / 2),
                    (self.map.DIM / 2) - (ydim / 2)))
            # 8  if yes - continue, if not go back to step 4

            # 9 add new room to map and list of rooms
                self.addRoom(self.map, newRoom, newRoom.getPos())
                rooms += [newRoom]

            # 9.a add rooms as neighbors
                candidateRoom.neighbors.append(newRoom)
                newRoom.neighbors.append(candidateRoom)
            # 9.b make room secret?
                if len(rooms) == maxRooms - 1:
                    newRoom.secret is True
                    self.secretRooms.append(newRoom)

            #10 create doorway into new room
                (x1, y1) = tile
                if dir in ['n', 's']:
                    if newRoom.secret:
                        self.map.setEntry(x1, y1, const.EWFAKE)
                    else:
                        self.map.setEntry(x1, y1, const.EWDOOR)
                else:
                    if newRoom.secret:
                        self.map.setEntry(x1, y1, const.NSFAKE)
                    else:
                        self.map.setEntry(x1, y1, const.NSDOOR)
                candidateRoom.entrances.append((x1, y1))
                (x2, y2) = dirDict[dir]
                if dir == 'n':
                    self.map.setEntry(x1 + x2 - 1, y1 + y2, const.URWALL)
                    self.map.setEntry(x1 + x2 + 1, y1 + y2, const.ULWALL)
                elif dir == 's':
                    self.map.setEntry(x1 + x2 - 1, y1 + y2, const.LRWALL)
                    self.map.setEntry(x1 + x2 + 1, y1 + y2, const.LLWALL)
                elif dir == 'e':
                    self.map.setEntry(x1 + x2, y1 + y2 - 1, const.LRWALL)
                    self.map.setEntry(x1 + x2, y1 + y2 + 1, const.URWALL)
                elif dir == 'w':
                    self.map.setEntry(x1 + x2, y1 + y2 - 1, const.LLWALL)
                    self.map.setEntry(x1 + x2, y1 + y2 + 1, const.ULWALL)
                self.map.setEntry(x1 + x2, y1 + y2, 0)
                newRoom.entrances.append((x1 + x2, y1 + y2))
            # 11 repeat step 4

        # set staircases
        '''
        choice1 = choice(rooms)
        (xpos, ypos) = choice1.getPos()
        (xdim, ydim) = choice1.getDimensions()
        self.map.setEntry( xpos + xdim/2, ypos + ydim/2, 120)
        self.POE = ( xpos + xdim/2, ypos + ydim/2 )
        rooms.remove(choice1)
        '''
        # down
        choice2 = choice(rooms)
        # find room with only 1 entrance
        # WARNING: this algorithm not guaranteed to stop.
        while len(choice2.entrances) > 1 or choice2.secret:
            choice2 = choice(rooms)
        (xpos, ypos) = choice2.getPos()
        (xdim, ydim) = choice2.getDimensions()
        (doorX, doorY) = choice2.entrances[0]
        self.map.setEntry(xpos + xdim / 2, ypos + ydim / 2, 121)
        self.map.setEntry(doorX, doorY, 116)
        self.map.pointOfExit = (xpos + xdim / 2, ypos + ydim / 2)

        # up
        choice1 = choice2.neighbors[0]
        (xpos, ypos) = choice1.getPos()
        (xdim, ydim) = choice1.getDimensions()
        self.map.setEntry(xpos + xdim / 2, ypos + ydim / 2, 120)
        self.map.pointOfEntry = (xpos + xdim / 2, ypos + ydim / 2)
        self.map.heroStart = (xpos + xdim / 2, ypos + ydim / 2)
        rooms.remove(choice1)

        rooms.remove(choice2)

        # add key for door
        keyRoom = choice(rooms)
        (xpos, ypos) = keyRoom.getPos()
        (xdim, ydim) = keyRoom.getDimensions()
        self.map.setEntry(xpos + xdim / 2, ypos + ydim / 2, 98)
        rooms.remove(keyRoom)

        # set hero starting location - optional
        choice3 = choice(rooms)
        (xpos, ypos) = choice3.getPos()
        (xdim, ydim) = choice3.getDimensions()
        self.map.hs = (xpos + xdim / 2, ypos + ydim / 2)
        rooms.remove(choice3)

        #add chests
        chestlist = []
        for i in range(maxRooms / 5):
            choice4 = choice(rooms)
            (xpos, ypos) = choice4.getPos()
            (xdim, ydim) = choice4.getDimensions()
            chestItems = []
            chestItems.append((const.PARCHMENT - const.FRUIT1,
                               choice(mapScr.parchByLevel[self.level])))
            if self.rollDie(0, 2):
                chestItems.append((13, choice(range(15, 50) + range(15, 30))))
            self.map.setEntry(xpos + xdim / 2, ypos + ydim / 2, 110)
            chestlist += [((xpos + xdim / 2, ypos + ydim / 2), chestItems)]
            rooms.remove(choice4)
        for room in self.secretRooms:
            (xpos, ypos) = room.getPos()
            (xdim, ydim) = room.getDimensions()
            self.map.setEntry(xpos + xdim / 2, ypos + ydim / 2, 110)
            chestlist += [((xpos + xdim / 2, ypos + ydim / 2),
                         [(randrange(26, 29), self.level / 4,
                         [randrange((self.level / 4) + 1,
                         (self.level / 4) + 3),
                         randrange((self.level / 4) + 1,
                         (self.level / 4) + 3),
                         randrange((self.level / 4) + 1,
                         (self.level / 4) + 3)])])]

        self.map.chests = dict(chestlist)
        # add enemies
        while len(rooms) > 0:
            room = choice(rooms)
            (xpos, ypos) = room.getPos()
            (xdim, ydim) = room.getDimensions()
            self.map.NPCs.append(((xpos + xdim / 2, ypos + ydim / 2),
                choice(mEnemyScr.enemiesByLevel[self.map.level])))
            rooms.remove(room)

    def addRoom(self, map, room, pos):
        map.copyText = room.grid
        map.mapPaste(pos)

    def getMapBall(self):
        return self.map.getMapBall()

    def draw(self):
        gridField.fill([0, 0, 0])
        for i in range(DIM):
            for j in range(DIM):
                gridField.blit(images.mapImages[myMap.getMapEntry(i, j)],
                    (i * blocksize, j * blocksize))

        screen.blit(gridField, (0, 0))
        pygame.display.flip()
        while (pygame.event.wait().type != pygame.KEYDOWN):
            pass