import pygame
from IMG import images
from UTIL import colors, const
import math

class Display():
    
    def __init__(self, screen):
        self.screen = screen
        images.load()
        self.images = images.mapImages
        self.fog = pygame.Surface( (30,30) )
        self.fog.fill( colors.black )

    # Takes first two coordinates of hero rect, gameBoard and
    # draws darkness
    def drawShade(self, map, gameBoard):
        (topX, topY) = map.topMapCorner
        (px, py) = map.playerXY
        tiles = map.litTiles
        for x in range( map.WINDOWSIZE ):
            for y in range( map.WINDOWSIZE ):
                if (x+topX, y+topY) in tiles:
                    self.fog.set_alpha( 0 )
                else:
                    self.fog.set_alpha( 140 )
                gameBoard.blit(self.fog, ( (x)*const.blocksize, (y)*const.blocksize), area=(0,0,const.blocksize,const.blocksize) )
    def redrawMap(self, map, heroLoc, heroRect, gameBoard):
        # Redraw map on screen from current map matrix
        #self.revealMap()
        (rx,ry,rx2,ry2) = heroRect
        rx = rx/const.blocksize
        ry = ry/const.blocksize
        (topX, topY), (oldTopX, oldTopY) = map.updateWindowCoordinates(heroLoc, heroRect)
        gameBoard.blit( self.getMapWindow( (topX, topY), map.WINDOWSIZE ), (map.WINDOWOFFSET,map.WINDOWOFFSET) )
        if map.type == 'dungeon':
            self.drawShade(map, gameBoard)
            #self.drawDarkness(rx, ry, gameBoard)
    # takes map coordinates, returns map window
    def getMapWindow(self, pos, wsize=10):
        (x1, y1) = pos
        window = pygame.Surface( (wsize*const.blocksize, wsize*const.blocksize) )
        window.blit( self.xGameBoard, ( -(x1*const.blocksize), -(y1*const.blocksize) ) )
        return window
    # takes pixel coordinates of top left corner of DIMxDIM window of xGameBoard, returns map window
    def getScrollingMapWindow(self, pos, wsize = 10, darkness=True):
        (x1,y1) = pos
        window = pygame.Surface( (wsize*const.blocksize, wsize*const.blocksize) )
        window.blit( self.xGameBoard, ( -x1, -y1 ) )
        #self.drawDarkness
        return window
    # draws entire map to DIMxDIM Surface
    def redrawXMap(self, map):
        self.xGameBoard = pygame.Surface( (map.getDIM()*const.blocksize, map.getDIM()*const.blocksize) )
        if map.type == 'dungeon':
            map.revealMap()
        for x in range(map.getDIM()):
            for y in range(map.getDIM()):
                tile = map.getEntry(x,y)
                if tile != const.VOID and map.visDict[(x,y)]:
                    if tile > 24:
                        shortList = [map.getEntry(tx, ty) for (tx, ty) in map.neighbors((x,y))]
                        if const.VOID not in shortList:
                            self.xGameBoard.blit( self.images[ map.defaultBkgd ], ( (x*const.blocksize), (y*const.blocksize) ) )
                    if map.getEntry(x, y) == const.ITEMSDOOR:
                        self.xGameBoard.blit( self.images[128], (x*const.blocksize - const.blocksize, y*const.blocksize - 2*const.blocksize), area = self.images[128].get_rect() )
                    else: self.xGameBoard.blit( self.images[ tile ], ( (x*const.blocksize), (y*const.blocksize) ) )
        if map.type == 'village':
            for s in map.shops:
                if map.shops[s][0] == 'itemshop':
                    (sX, sY) = s
                    self.xGameBoard.blit( self.images[128], (sX*const.blocksize - const.blocksize, sY*const.blocksize - (2*const.blocksize)) )
                if map.shops[s][0] == 'magicshop':
                    (sX, sY) = s
                    self.xGameBoard.blit( self.images[129], (sX*const.blocksize - const.blocksize, sY*const.blocksize - (2*const.blocksize)) )
                if map.shops[s][0] == 'blacksmith':
                    (sX, sY) = s
                    self.xGameBoard.blit( self.images[130], (sX*const.blocksize - const.blocksize, sY*const.blocksize - (2*const.blocksize)) )
                if map.shops[s][0] == 'armory':
                    (sX, sY) = s
                    self.xGameBoard.blit( self.images[131], (sX*const.blocksize - const.blocksize, sY*const.blocksize - (2*const.blocksize)) )
                if map.shops[s][0] == 'tavern':
                    (sX, sY) = s
                    self.xGameBoard.blit( self.images[132], (sX*const.blocksize - const.blocksize, sY*const.blocksize - (3*const.blocksize)) )
    
    # called immediately after player makes a move or arrives in a new level
    # takes x,y of old myHero.rect location and finds new
    def drawHero(self, hero, map, gameBoard, game=None, dir=None, animated=True):
        DIMEN = map.getDIM()
        (newX,newY) = hero.getXY()
        (oldX, oldY, c, d) = hero.getRect()
        scrolling = False
        if DIMEN > const.HALFDIM:
            if (5*const.blocksize < newX <= (DIMEN-5)*const.blocksize):
                newX = 5 * const.blocksize
                if dir in ['left','right'] and oldX == 5*const.blocksize:
                    scrolling = True
            if newX > (DIMEN-5)*const.blocksize:
                newX = newX - int( math.ceil( float(DIMEN)/2.) )*const.blocksize
            if (5*const.blocksize < newY <= (DIMEN-5)*const.blocksize):
                newY = 5 * const.blocksize
                if dir in ['up','down'] and oldY == 5*const.blocksize:
                    scrolling = True
            if newY > (DIMEN-5)*const.blocksize:
                newY = newY - int( math.ceil( float(DIMEN)/2.) )*const.blocksize
        else:
            newX += (const.HALFDIM - DIMEN)/2*const.blocksize
            newY += (const.HALFDIM - DIMEN)/2*const.blocksize
        
       
        #make the move animated
        if animated:
            if dir == None:
                scrolling = False
            else: scrollX , scrollY = const.scrollingDict[dir]
            (px,py) = hero.getXY()
            pos, oldPos = map.updateWindowCoordinates( hero.getXY(), hero.getRect() )
            (topX, topY) = pos
            if oldX == newX:
                xAxis = [oldX]*const.blocksize
            elif oldX < newX:
                xAxis = range(oldX, newX)
            else:
                xAxis = range(oldX, newX, -1)
            if oldY == newY:
                yAxis = [oldY]*const.blocksize
            elif oldY < newY:
                yAxis = range(oldY, newY)
            elif oldY > newY:
                yAxis = range(oldY, newY, -1)
            for (idx, (i, j)) in list( enumerate(zip(xAxis, yAxis), start=1) ):
                
                #game.clock.tick(100)
                hero.setRect( i, j, const.blocksize, const.blocksize)
                for npc in game.NPCs:
                    if npc.moving:
                        npc.shiftOnePixel(npc.dir, -1)
                        if (idx % 2 == 0): npc.takeStep()
                if scrolling:
                    for npc in game.NPCs:
                        npc.shiftOnePixel(dir, 1)
                    
                    gameBoard.blit( self.getScrollingMapWindow( ( (topX*const.blocksize)+(idx*scrollX)-(const.blocksize*scrollX), (topY*const.blocksize)+(idx*scrollY)-(const.blocksize*scrollY) ) ), (0,0) )
                    
                    if map.type == 'dungeon':
                        self.drawShade( map, gameBoard )
                        #self.myMap.drawDarkness( newX/blocksize, newY/blocksize, self.gameBoard )
                else: self.redrawMap(map, hero.getXY(), hero.getRect(), gameBoard)
                if (idx % 2 == 0) and hero.moving: hero.takeStep()
                game.displayGameBoard()
        
        for npc in game.NPCs:
            npcdir = npc.dir
            (cX, cY) = npc.getXY()
            (tX, tY) = map.topMapCorner
            (oRX, oRY, oRX2, oRY2) = npc.getRect()
            nRX = cX*const.blocksize-(tX*const.blocksize)
            nRY = cY*const.blocksize-(tY*const.blocksize)
            npc.setRect(nRX, nRY, const.blocksize, const.blocksize)
            npc.moving = False
        hero.setRect( newX, newY, const.blocksize, const.blocksize)
        
    def drawNPC(self, npc, map, game, animated=False):
        dir = npc.dir
        (cX, cY) = npc.getXY()
        (tX, tY) = map.topMapCorner
        (oRX, oRY, oRX2, oRY2) = npc.getRect()
        nRX = cX*const.blocksize-(tX*const.blocksize)
        nRY = cY*const.blocksize-(tY*const.blocksize)
        '''
        if npc.moving:
            if oRX == nRX:
                xAxis = [oRX]*const.blocksize
            elif oRX < nRX:
                xAxis = range(oRX, nRX)
            else:
                xAxis = range(oRX, nRX, -1)
            if oRY == nRY:
                yAxis = [oRY]*const.blocksize
            elif oRY < nRY:
                yAxis = range(oRY, nRY)
            elif oRY > nRY:
                yAxis = range(oRY, nRY, -1)
            for (idx, (i, j)) in list( enumerate(zip(xAxis, yAxis), start=1) ):
                game.clock.tick(120)
                npc.shiftOnePixel(dir, -1)
                if (idx % 2 == 0): npc.takeStep()
                self.redrawMap(map, game.myHero.getXY(), game.myHero.getRect(), game.gameBoard)
                game.displayGameBoard()
        '''
        npc.setRect(nRX, nRY, const.blocksize, const.blocksize)
        npc.moving = False