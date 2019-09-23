# Created on 8/28/2019

from gameDriver import GameDriver
from theme import Theme
import pygame, sys

dim = (15, 10)
if dim[0] < 4 or dim[1] <= 0:
    print("Invalid Squares Per Row/Column")
    sys.exit(0)

width = 50
if width <= 0:
    print("Invalid Square Width")
    sys.exit(0)

# Bomb img, flag img, font name
normal = Theme("explosion.png", "flag_0.png", "Arial", width)
american = Theme("firework.png", "flag_1.png", "Comic Sans", width)
traditional = Theme("bomb_2.png", "flag_2.png", "Times New Roman", width)

driver = GameDriver(dim, width, traditional)

playing = True
old_time = pygame.time.get_ticks()
while True:
    dt = pygame.time.get_ticks() - old_time
    old_time = pygame.time.get_ticks()

    events = pygame.event.get()

    if playing:
        playing = driver.playGame(dim, width, events, dt)

    if driver.restart(events):
        playing = True

    pygame.display.update()
