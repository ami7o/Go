import pygame
from pygame.locals import *
import os
import sys
import time
import random
import numpy as np
import tkinter as tk
from tkinter import messagebox, simpledialog

root = tk.Tk()
root.withdraw()

# pygame settings
FPS = 100
pygame.init()
fpsClock=pygame.time.Clock()

GRIDSIZE = 32
SIZE = 19
MARGIN = 32
MENU = 120
screen = pygame.display.set_mode((GRIDSIZE * (SIZE - 1) + MARGIN * 2 + MENU, \
     GRIDSIZE * (SIZE - 1) + MARGIN * 2), 0, 32)
surface = pygame.Surface(screen.get_size())
surface = surface.convert()
surface.fill((255,128,0))
clock = pygame.time.Clock()

pygame.key.set_repeat(1, 40)

screen.blit(surface, (0,0))

BLACK = (0, 0, 0)
RED = (255, 0, 0)
EMPTY, BLACK, WHITE = 0, 1, 2
DIRECTIONS = ((1, 0), (-1, 0), (0, 1), (0, -1))

# initialize images and buttons
BUTTON_DIAMETER = 100
BUTTON_WIDTH, BUTTON_HEIGHT = 120, 60
blackImg = pygame.image.load('images/black.png')
whiteImg = pygame.image.load('images/white.png')
offImg = pygame.image.load('images/switch_off.png')
onImg = pygame.image.load('images/switch_on.png')
resetImg = pygame.image.load('images/reset.png')
undoImg = pygame.image.load('images/undo.png')
saveImg = pygame.image.load('images/save.png')

images = []
images.append(pygame.transform.scale(blackImg, (GRIDSIZE, GRIDSIZE)))
images.append(pygame.transform.scale(whiteImg, (GRIDSIZE, GRIDSIZE)))

buttons = []
buttons.append(pygame.transform.scale(blackImg, (BUTTON_DIAMETER, BUTTON_DIAMETER)))
buttons.append(pygame.transform.scale(whiteImg, (BUTTON_DIAMETER, BUTTON_DIAMETER)))
buttons.append(pygame.transform.scale(offImg, (BUTTON_WIDTH, BUTTON_HEIGHT)))
buttons.append(pygame.transform.scale(onImg, (BUTTON_WIDTH, BUTTON_HEIGHT)))
buttons.append(pygame.transform.scale(resetImg, (BUTTON_WIDTH, BUTTON_HEIGHT)))
buttons.append(pygame.transform.scale(undoImg, (BUTTON_WIDTH, BUTTON_HEIGHT)))
buttons.append(pygame.transform.scale(saveImg, (BUTTON_WIDTH, BUTTON_HEIGHT)))

button_positions = []
button_positions.append((630, 50))
button_positions.append((630, 180))
button_positions.append((620, 300))
button_positions.append((620, 300))
button_positions.append((620, 380))
button_positions.append((620, 460))
button_positions.append((620, 540))

# return real position given x y
def getPosition(x, y):
    return (MARGIN + x * GRIDSIZE, MARGIN + y * GRIDSIZE)

# return x y given real position
def getXY(mouseX, mouseY):
    x = round((mouseX - MARGIN) / GRIDSIZE)
    y = round((mouseY - MARGIN) / GRIDSIZE)
    return x, y

# check if x and y are valid on the board
def checkXY(x, y):
    return 0 <= x < SIZE and 0 <= y < SIZE

# return distance from (x1, y1) to (x2, y2)
def getDistance(x1, y1, x2, y2):
    return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

# draw buttons
def drawButton(mode):
    for i in range(2):
        screen.blit(buttons[i], button_positions[i])
    (redX, redY) = button_positions[mode - 1]
    pygame.draw.circle(screen, RED, (redX + BUTTON_DIAMETER / 2, redY + BUTTON_DIAMETER / 2), 10)
    screen.blit(buttons[3 if switch else 2], button_positions[2])
    for i in range(4, len(buttons)): # rest of buttons
        screen.blit(buttons[i], button_positions[i])

# draw board
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

# eat from (x, y) that has the given color
def eat(grid, x, y, color):
    if checkXY(x, y):
        if grid[x][y] == color:
            grid[x][y] = EMPTY
            for d in DIRECTIONS:
                eat(grid, x + d[0], y + d[1], color)

# return true if we can eat from (x, y) that has the given color
def checkEat2(grid, x, y, color, visited):
    if checkXY(x, y) and (x, y) not in visited:
        if grid[x][y] == EMPTY:
            return False
        elif grid[x][y] == color:
            visited.add((x, y))
            for d in DIRECTIONS:
                if not checkEat2(grid, x + d[0], y + d[1], color, visited):
                    return False
    return True

# check eat and perform eat from (x, y) with the color
def checkEat(grid, x, y, color):
    if checkXY(x, y) and checkEat2(grid, x, y, color, set()):
        eat(grid, x, y, color)

# auto check eat given where the stone is placed and its color
def autoCheck(grid, x, y, color):
    # check the other color
    for d in DIRECTIONS:
        checkEat(grid, x + d[0], y + d[1], 3 - color)
    # check this color
    checkEat(grid, x, y, color)

# check if mouse is on the button with the given index
def checkButton(mouseX, mouseY, index):
    return button_positions[index][0] <= mouseX <= button_positions[index][0] + BUTTON_WIDTH \
        and button_positions[index][1] <= mouseY <= button_positions[index][1] + BUTTON_HEIGHT


def addHistory(history, index, grid):
    temp = history[:index+1]
    temp.append(grid.copy())
    return temp

if __name__ == '__main__':
    grid = np.zeros((SIZE, SIZE))
    mode = BLACK
    check = True
    switch = True
    drawBoard(grid, mode, switch)
    history = [grid.copy()]
    index = 0
    
    while True:
        ev = pygame.event.get()
        # proceed events
        for event in ev:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouseX, mouseY = pygame.mouse.get_pos()
                x, y = getXY(mouseX, mouseY)
                if checkXY(x, y): # pressed board
                    if grid[x][y] == EMPTY: # put stone
                        grid[x][y] = mode
                        if (check):
                            autoCheck(grid, x, y, mode)
                        if (switch):
                            mode = 3 - mode
                    else: # remove stone
                        grid[x][y] = EMPTY
                    history = addHistory(history, index, grid)
                    index += 1
                    drawBoard(grid, mode, switch)
                else: # pressed outside the board
                    # find distance to 
                    blackDis = getDistance(button_positions[0][0] + BUTTON_DIAMETER / 2, \
                        button_positions[0][1] + BUTTON_DIAMETER / 2, mouseX, mouseY)
                    whiteDis = getDistance(button_positions[1][0] + BUTTON_DIAMETER / 2, \
                        button_positions[1][1] + BUTTON_DIAMETER / 2, mouseX, mouseY)
                    if blackDis <= BUTTON_DIAMETER / 2: # black stone
                        mode = BLACK
                        drawButton(mode)
                    elif whiteDis <= BUTTON_DIAMETER / 2: # white stone
                        mode = WHITE
                        drawButton(mode)
                    elif checkButton(mouseX, mouseY, 2): # switch
                        switch = not switch
                        drawButton(mode)
                    elif checkButton(mouseX, mouseY, 4): # reset
                        MsgBox = messagebox.askquestion('Warning', 'Are you sure you want to reset?', icon = 'warning')
                        if MsgBox == 'yes':
                            grid = np.zeros((SIZE, SIZE))
                            drawBoard(grid, mode, switch)
                            history = addHistory(history, index, grid)
                            index += 1
                    elif checkButton(mouseX, mouseY, 5): # undo/redo
                        if mouseX <= button_positions[5][0] + BUTTON_WIDTH / 2: # undo
                            if index > 0:
                                index -= 1
                                grid = history[index].copy()
                                drawBoard(grid, mode, switch)
                        else: # redo
                            if index < len(history) - 1:
                                index += 1
                                grid = history[index].copy()
                                drawBoard(grid, mode, switch)
                    elif checkButton(mouseX, mouseY, 6): # save/load
                        if mouseX <= button_positions[6][0] + BUTTON_WIDTH / 2: # save
                            filename = simpledialog.askstring('Save', 'Enter filename to save')
                            if filename != None:
                                with open(f'saved/{filename}.npy', 'wb') as f:
                                    np.save(f, np.array(grid))
                                messagebox.showinfo('Saved', f'Successfully saved to saved/{filename}.npy')
                        else: # load
                            filename = simpledialog.askstring('Load', 'Enter filename to load')
                            if os.path.exists(f'saved/{filename}.npy'):
                                with open(f'saved/{filename}.npy', 'rb') as f:
                                    grid = np.load(f)
                                drawBoard(grid, mode, switch)
                                history = addHistory(history, index, grid)
                                index += 1
                            else:
                                messagebox.showerror('Not found', f'saved/{filename}.npy does not exist')
            elif event.type == pygame.QUIT:
                pygame.quit()
                exit()

        pygame.display.flip()
        pygame.display.update()
        fpsClock.tick(FPS)