# Created on 8/28/2019

from gameDriver import GameDriver, playAgain

dim = (1025, 725)
width = 50

driver = GameDriver()

while True:
    driver.setDisplay(dim, width)

    won = driver.playGame(width)

    if not playAgain(200, 100, won):
        break
