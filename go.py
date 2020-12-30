import pygame
import sys
import time
import random
import numpy as np
import tkinter as tk
from tkinter import messagebox

from pygame.locals import *

FPS = 5
pygame.init()
fpsClock=pygame.time.Clock()

GRIDSIZE = 32
SIZE = 19
MARGIN = 32
MENU = 100
screen = pygame.display.set_mode((GRIDSIZE * (SIZE - 1) + MARGIN * 2 + MENU, \
     GRIDSIZE * (SIZE - 1) + MARGIN * 2), 0, 32)
surface = pygame.Surface(screen.get_size())
surface = surface.convert()
surface.fill((255,128,0))
clock = pygame.time.Clock()

pygame.key.set_repeat(1, 40)

root = tk.Tk()
root.withdraw()

screen.blit(surface, (0,0))

BLACK = (0, 0, 0)
RED = (255, 0, 0)
EMPTY, BLACK, WHITE = 0, 1, 2

blackImg = pygame.image.load('images/black.png')
whiteImg = pygame.image.load('images/white.png')
offImg = pygame.image.load('images/switch_off.png')
onImg = pygame.image.load('images/switch_on.png')
resetImg = pygame.image.load('images/reset.png')
images = []
images.append(pygame.transform.scale(blackImg, (GRIDSIZE, GRIDSIZE)))
images.append(pygame.transform.scale(whiteImg, (GRIDSIZE, GRIDSIZE)))

buttons = []
buttons.append(pygame.transform.scale(blackImg, (100, 100)))
buttons.append(pygame.transform.scale(whiteImg, (100, 100)))
buttons.append(pygame.transform.scale(offImg, (120, 60)))
buttons.append(pygame.transform.scale(onImg, (120, 60)))
buttons.append(pygame.transform.scale(resetImg, (120, 60)))

button_positions = []
button_positions.append((620, 50))
button_positions.append((620, 200))
button_positions.append((620, 400))
button_positions.append((620, 500))

def getPosition(x, y):
    return (MARGIN + x * GRIDSIZE, MARGIN + y * GRIDSIZE)

def getXY(mouseX, mouseY):
    x = round((mouseX - MARGIN) / GRIDSIZE)
    y = round((mouseY - MARGIN) / GRIDSIZE)
    return x, y

def checkXY(x, y):
    return x in range(SIZE) and y in range(SIZE)

def getDistance(x1, y1, x2, y2):
    return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def drawButton(mode):
    for i in range(2):
        screen.blit(buttons[i], button_positions[i])
    (redX, redY) = button_positions[mode - 1]
    pygame.draw.circle(screen, RED, (redX + 50, redY + 50), 10)

def drawBoard(grid, mode, switch):
    # draw grids
    for x in range(0, SIZE):
        pygame.draw.line(surface, BLACK, getPosition(x, 0), getPosition(x, SIZE - 1))
        pygame.draw.line(surface, BLACK, getPosition(0, x), getPosition(SIZE - 1, x))

    # draw dots
    for x in range(3, SIZE, 6):
        for y in range(3, SIZE, 6):
            pygame.draw.circle(surface, BLACK, getPosition(x, y), 3)

    screen.blit(surface, (0, 0))

    # draw stones
    for x in range(SIZE):
        for y in range(SIZE):
            if grid[x][y] != EMPTY:
                screen.blit(images[int(grid[x][y] - 1)], getPosition(x - 0.5, y - 0.5))

    drawButton(mode)
    screen.blit(buttons[3 if switch else 2], button_positions[2])
    screen.blit(buttons[4], button_positions[3])

if __name__ == '__main__':
    prevEvent = pygame.MOUSEBUTTONDOWN
    grid = np.zeros((SIZE, SIZE))
    mode = BLACK
    switch = True
    drawBoard(grid, mode, switch)
    
    while True:
        ev = pygame.event.get()
        # proceed events
        for event in ev:
            if event.type == pygame.MOUSEBUTTONDOWN:
                prevEvent = event.type
            elif event.type == pygame.MOUSEBUTTONUP:
                prevEvent = event.type
                mouseX, mouseY = pygame.mouse.get_pos()
                x, y = getXY(mouseX, mouseY)
                if checkXY(x, y):
                    if grid[x][y] == EMPTY:
                        grid[x][y] = mode
                        screen.blit(images[mode - 1], getPosition(x - 0.5, y - 0.5))
                        if (switch):
                            mode = 3 - mode
                            drawButton(mode)
                    else:
                        grid[x][y] = EMPTY
                        drawBoard(grid, mode, switch)
                else:
                    blackDis = getDistance(*button_positions[0], *pygame.mouse.get_pos())
                    whiteDis = getDistance(*button_positions[1], *pygame.mouse.get_pos())
                    if blackDis <= 100:
                        mode = BLACK
                        drawButton(mode)
                    elif whiteDis <= 100:
                        mode = WHITE
                        drawButton(mode)
                    elif mouseX in range(620, 740) and mouseY in range(400, 460):
                        switch = not switch
                        screen.blit(buttons[3 if switch else 2], button_positions[2])
                    elif mouseX in range(620, 740) and mouseY in range(500, 660): # reset
                        MsgBox = messagebox.askquestion('Warning', 'Are you sure you want to reset?', icon = 'warning')
                        if MsgBox == 'yes':
                            prevEvent = pygame.MOUSEBUTTONDOWN
                            grid = np.zeros((SIZE, SIZE))
                            mode = BLACK
                            switch = True
                            drawBoard(grid, mode, switch)
            elif event.type == pygame.QUIT:
                pygame.quit()
                exit()

        pygame.display.flip()
        pygame.display.update()
        fpsClock.tick(FPS)