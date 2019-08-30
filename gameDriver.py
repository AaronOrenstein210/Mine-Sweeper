# Created on 8/27/2019

import pygame, sys
from pygame.locals import *
from square import Square
from random import randint

pygame.init()


class GameDriver:
    # init
    def __init__(self):
        self.display = pygame.display
        self.game_board = pygame.Rect
        self.squares = []
        self.font = pygame.font

    # Set the display
    def setDisplay(self, dim, width):
        self.display = pygame.display.set_mode((dim[0], dim[1]))
        pygame.display.set_caption("Game")

        num_cols = int(dim[0] / width)
        num_rows = int(dim[1] / width)
        extra_w = dim[0] % width
        extra_h = dim[1] % width
        self.game_board = pygame.Rect(extra_w / 2, extra_h / 2, dim[0] - extra_w, dim[1] - extra_h)

        # Get locations of bombs
        bomb_coords = self.getBombs(num_rows, num_cols)
        # Set up individual squares
        self.setUpSquares(width, bomb_coords)

        # Scale font to fit inside the inner square
        self.font = getScaledFont(width * 19 / 20, width * 19 / 20, "0")

        # Draw the squares
        for row in self.squares:
            for s in row:
                s.draw(self.display)
                # Reveals board
                # s.onClick(display, True, font)

    # Returns coordinates of bombs
    def getBombs(self, num_rows, num_cols):
        # Generate bomb locations
        num_squares = num_cols * num_rows
        num_bombs = int(num_squares / 4)
        bomb_coords = []
        for i in range(num_bombs):
            coord = randCoord(0, 0, num_cols, num_rows)
            # Find a new location and add it to our list
            while coord in bomb_coords:
                coord = randCoord(0, 0, num_cols, num_rows)
            bomb_coords.append(coord)
        return bomb_coords

    # Sets up the squares, either as a bomb or a number
    def setUpSquares(self, width, bomb_coords):
        num_rows = int(self.game_board.height / width)
        num_cols = int(self.game_board.width / width)
        # Generate squares
        self.squares.clear()
        for y in range(num_rows):
            row = []
            for x in range(num_cols):
                # For every square, initialize it and tell it if it is a bomb
                square = Square(Rect((x * width) + self.game_board.left,
                                     (y * width) + self.game_board.top,
                                     width, width),
                                (x, y) in bomb_coords)
                # If it isn't a bomb, figure out its number value
                if not square.is_bomb:
                    bomb_count = 0
                    for y1 in range(y - 1, y + 2):
                        for x1 in range(x - 1, x + 2):
                            if (x1, y1) in bomb_coords:
                                bomb_count += 1
                    square.val = bomb_count
                row.append(square)
            self.squares.append(row)

    # Runs game
    def playGame(self, width):
        # Run game
        while True:
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONUP:
                    if event.button == BUTTON_LEFT or event.button == BUTTON_RIGHT:
                        # Get click position
                        pos = pygame.mouse.get_pos()
                        if self.game_board.collidepoint(pos):
                            pos = (pos[0] - self.game_board.left, pos[1] - self.game_board.top)
                            x, y = int(pos[0] / width), int(pos[1] / width)
                            if self.squares[y][x].onClick(self.display,
                                                          event.button == BUTTON_LEFT,
                                                          self.font):
                                return False
                            elif event.button == BUTTON_LEFT:
                                # Check if there are zeroes that can be exposed
                                zero_coords = []
                                self.findZeroes(x, y, zero_coords)
                                for x, y in zero_coords:
                                    self.squares[y][x].onClick(self.display, True, self.font)
                        if self.haveWon():
                            return True
                elif event.type == QUIT:
                    pygame.quit()
                    sys.exit()
            pygame.display.update()

    # Recursive function that reveals any zeroes near the selected square
    # Also reveals all squares outside those zeroes (So the player doesn't have to)
    def findZeroes(self, x, y, zero_coords):
        new_coords = []
        for y1 in range(y - 1, y + 2):
            for x1 in range(x - 1, x + 2):
                if 0 <= x1 < len(self.squares[0]) and 0 <= y1 < len(self.squares):
                    square = self.squares[y1][x1]
                    if (x1, y1) not in zero_coords and not square.is_clicked \
                            and (square.val is 0 or self.squares[y][x].val is 0):
                        zero_coords.append((x1, y1))
                        new_coords.append((x1, y1))
        for p in new_coords:
            if self.squares[p[1]][p[0]].val == 0:
                self.findZeroes(p[0], p[1], zero_coords)

    # Checks if we have won
    def haveWon(self):
        for row in self.squares:
            for s in row:
                # Check if a square should or shouldn't
                should_flag = s.is_bomb and not s.is_flagged
                shouldnt_flag = not s.is_bomb and s.is_flagged
                if should_flag or shouldnt_flag:
                    return False
        return True


# Gets the biggest font that fits the text within max_w and max_H
def getScaledFont(max_w, max_h, text):
    font_size = 0
    font = pygame.font.SysFont("Times New Roman", font_size)
    w, h = font.size(text)
    while w < max_w and h < max_h:
        font_size += 1
        font = pygame.font.SysFont("Times New Roman", font_size)
        w, h = font.size(text)
    return pygame.font.SysFont("Times New Roman", font_size - 1)


# Generates a random coord with minX <= x < maxX and minY <= y < maxY
def randCoord(minX, minY, maxX, maxY):
    return (randint(minX, maxX - 1), randint(minY, maxY - 1))


def playAgain(w, h, won):
    color = (0, 255, 0) if won else (255, 0, 0)
    say1 = "You Won" if won else "You Lost"
    say2 = "Play Again?"

    # Set up display
    display = pygame.display.set_mode((w, h))
    pygame.display.set_caption("Play Again?")

    # Set up text
    pygame.draw.rect(display, (0, 0, 0), pygame.Rect(0, 0, w / 2, h / 2))
    font = getScaledFont(w, h / 4, say2)

    # Draw first line
    text = font.render(say1, 1, color)
    text_rect = text.get_rect(center=(w / 2, h / 8))
    display.blit(text, text_rect)

    # Draw second line
    text = font.render(say2, 1, (0, 128, 255))
    text_rect = text.get_rect(center=(w / 2, h * 3 / 8))
    display.blit(text, text_rect)

    w2 = w * 3 / 8
    h2 = h * 3 / 8
    pygame.draw.rect(display, (0, 255, 0), pygame.Rect(w / 16, h * 9 / 16, w2, h2))
    pygame.draw.rect(display, (255, 0, 0), pygame.Rect(w * 9 / 16, h * 9 / 16, w2, h2))

    # Run while loop
    while True:
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                if event.button == BUTTON_LEFT or event.button == BUTTON_RIGHT:
                    # Get click position
                    pos = pygame.mouse.get_pos()
                    if pos[1] >= h / 2:
                        return pos[0] < w / 2
            elif event.type == QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()
