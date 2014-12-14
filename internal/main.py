#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ransack-python

Ransack - a Python based roguelike
"""
import pygame
import game
import random
import cPickle
import gzip
import os
from UTIL import const, colors, load_image
from DISPLAY import effects
from HERO import creator
from OBJ import weapon

# Set the height and width of the screen
screenSize = [600, 600]
screen = pygame.display.set_mode(screenSize)
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)

if not pygame.font:
    print 'Warning, fonts disabled'

pygame.display.set_caption("Ransack")

pygame.init()
pygame.key.set_repeat(100, 100)
clock = pygame.time.Clock()
random.seed(os.urandom(1))

FX = effects.effects(clock, screen)

C = creator.Creator()

images = range(3)
images[0], r = load_image.load_image('cursor.bmp', -1)


def getFile():
    saveFiles = range(3)
    desc = range(3)
    for i in range(3):
        if os.access("ransack" + str(i) + ".sav", os.F_OK):
            peekFile = gzip.GzipFile("ransack" + str(i) + ".sav", 'rb')
            ball = cPickle.load(peekFile)
            peekFile.close()
            desc[i] = 'Saved game {} Level {} {} Days {}:{}.{}'.format(
                i, ball[1][11], ball[0].getDays(), ball[0].getHours() % 24,
                ball[0].getMins() % 60, ball[0].getSecs())
            saveFiles[i] = "ransack" + str(i) + ".sav"
        else:
            saveFiles[i] = 'No file'
            desc[i] = 'No file'

    saveBox = pygame.Surface((300, 100))
    selection = 0
    while True:
        saveBox.fill(colors.gold)
        if pygame.font:
            font = pygame.font.Font("./FONTS/gothic.ttf", 14)
            for i in range(3):
                saveBox.blit(font.render(desc[i], 1,
                                         colors.white,
                                         colors.gold),
                                         (25, i * 25))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                os.sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selection -= 1
                    if selection == -1:
                        selection = 2
                if event.key == pygame.K_DOWN:
                    selection += 1
                    if selection == 3:
                        selection = 0
                if event.key == pygame.K_RETURN:
                    return "ransack" + str(selection) + ".sav"
                if event.key == pygame.K_ESCAPE:
                    return None
        saveBox.blit(images[0], (0, selection * 25))
        screen.blit(saveBox, (100, 200))
        pygame.display.flip()


def endScreen(game, msg):
    dScreen = pygame.Surface((300, 300))
    if pygame.font:
        font = pygame.font.Font("./FONTS/SpinalTfanboy.ttf", 72)
        dScreen.blit(font.render(msg, 1, colors.red, colors.black), (50, 50))
        font = pygame.font.Font("./FONTS/devinne.ttf", 18)
        if game.myHero.level < 5:
            dScreen.blit(font.render("Nice Try, loser!", 1,
                                     colors.white,
                                     colors.black),
                                     (50, 125))
        elif game.myHero.level >= 5 and game.myHero.level < 10:
            dScreen.blit(font.render("Not bad... for a beginner!", 1,
                                      colors.white,
                                      colors.black),
                                      (50, 125))
        font = pygame.font.Font("./FONTS/gothic.ttf", 18)
        dScreen.blit(font.render("Level reached: " + str(game.myHero.level), 1,
                                  colors.white,
                                  colors.black),
                                  (50, 225))
        font = pygame.font.Font("./FONTS/gothic.ttf", 14)
        dScreen.blit(font.render(str(game.Ticker.getDays()) + "days, "
                                  + str(game.Ticker.getHours() % 24)
                                  + ":" + str(game.Ticker.getMins() % 60)
                                  + "." + str(game.Ticker.getSecs()), 1,
                                  colors.white,
                                  colors.black),
                                  (50, 250))
        screen.blit(dScreen, (const.gameBoardOffset, const.gameBoardOffset))
        pygame.display.flip()
    while (pygame.event.wait().type != pygame.KEYDOWN):
        pass


def main():
    titleScreen = pygame.Surface(screenSize)
    titleImg, titleRect = load_image.load_image('titlescreen.bmp', None)
    titleScreen.blit(titleImg, (0, 0))
    selection = 0
    options = ['Begin New Game', 'Load Saved Game', 'ExiT']
    screen.blit(titleScreen, (0, 0))
    while True:
        menuBox = pygame.Surface((300, 300))
        menuBox.fill(colors.black)
        menuBox.set_colorkey(colors.black)
        clock.tick(20)

        if pygame.font:
            font = pygame.font.Font("./FONTS/SpinalTfanboy.ttf", 48)
            for i in range(len(options)):
                line = font.render(options[i], 1, colors.white, colors.black)
                menuBox.blit(line, (30, (i * line.get_height())))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                os.sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    os.sys.exit()
                if event.key == pygame.K_UP:
                    selection -= 1
                    if selection == -1:
                        selection = len(options) - 1
                if event.key == pygame.K_DOWN:
                    selection += 1
                    if selection == len(options):
                        selection = 0
                if event.key == pygame.K_RETURN:
                    if options[selection] == 'Begin New Game':
                        newGame = game.game(screen, clock, FX,
                                            loadHero=C.mainLoop(screen))
                        FX.fadeOut(0)
                        if newGame.mainLoop():
                            endScreen(newGame, "You Win!")
                        else:
                            endScreen(newGame, "Game Over.")
                        FX.fadeOut(const.gameBoardOffset)
                    elif options[selection] == 'Load Saved Game':
                        try:
                            loadFile = getFile()
                            if loadFile is None:
                                pass
                            else:
                                savFile = gzip.GzipFile(loadFile, 'rb')
                                ball = cPickle.load(savFile)
                                savFile.close()
                                Game = game.game(screen, clock, FX,
                                                 loadTicker=ball[0],
                                                 loadHero=ball[1],
                                                 loadDungeon=ball[2],
                                                 loadDirector=ball[3],
                                                 currentMap=ball[4],
                                                 levelDepth=ball[5])
                                FX.fadeOut(0)
                                if Game.mainLoop():
                                    endScreen(Game, "You Win!")
                                else:
                                    endScreen(Game, "Game Over.")
                                FX.fadeOut(const.gameBoardOffset)
                        except IOError, e:
                            print 'File I/O error', e
                    elif options[selection] == 'ExiT':
                        FX.fadeOut(0)
                        os.sys.exit()

        menuBox.blit(images[0], (0, selection * line.get_height()
                                 + (line.get_height() / 2)))
        titleScreen.blit(titleImg, (0, 0))
        titleScreen.blit(menuBox, (200, 375))
        screen.blit(titleScreen, (0, 0))
        pygame.display.flip()

if __name__ == '__main__':
    main()