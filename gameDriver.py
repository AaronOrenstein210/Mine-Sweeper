# Created on 8/27/2019

import pygame, sys
from pygame.locals import *
from square import Square, getImg
from textView import TextView, getScaledFont
from random import randint

pygame.init()


# Lifecycle:
# 1) init() // Called one time only
# 2) startGame() // Called once each game at the beginning
# 3) playGame() // Called at every update while playing
#               // until the player loses/wins
# 4) restart() // Called at every update after winning/losing
#              // until player exits/restarts
# 5a) restart() returns true, go to 2) // Activated by player action
# 5b) player exits, game ends
class GameDriver:
    # Lifecycle functions
    # Initialize display
    def __init__(self, dim, width, theme):
        w = (dim[0] + 1) * width
        h = (dim[1] + 2) * width
        self.display = pygame.display.set_mode((w, h))
        pygame.display.set_caption("Kablooey")

        self.theme = theme

        # Draw top bar
        pygame.draw.rect(self.display, (128, 128, 128), Rect(width / 2, width / 4, w - width, width))
        self.bomb_counter = TextView(Rect(width * 3 / 4, width / 2, width, width / 2))
        self.bomb_counter.setFont(theme.font_name)
        self.bomb_counter.displayText("(:", self.display)
        self.timer = TextView(Rect(w - (width * 7 / 4), width / 2, width, width / 2))
        self.timer.setFont(theme.font_name)
        self.timer.displayText(":)", self.display)

        # Draw face
        self.face = Rect((w - width) / 2, width / 4, width, width)
        self.setFace(None)

        # Setup gameboard and squares
        self.game_board = Rect(width / 2, width * 3 / 2, dim[0] * width, dim[1] * width)
        self.squares = []
        self.setUpSquares(width)

        self.play_time = 0
        self.first = True

    # Runs game, returns true if still playing. false otherwise
    def playGame(self, dim, width, events, dt):
        playing = True
        # Run game
        for event in events:
            # We clicked
            if event.type == MOUSEBUTTONUP:
                # Get click position
                pos = pygame.mouse.get_pos()
                # Check if the click is in the game board
                if self.game_board.collidepoint(pos):
                    # Get the square that was clicked
                    pos = (pos[0] - self.game_board.left, pos[1] - self.game_board.top)
                    x, y = int(pos[0] / width), int(pos[1] / width)

                    if self.first:
                        self.first = False
                        self.play_time = 0
                        # Set bombs
                        self.setBombs(dim[1], dim[0], (x, y))

                    s = self.squares[y][x]

                    # Only left click if the square hasn't been clicked and isn't flagged
                    left_conditions = not (s.is_flagged or s.is_clicked)
                    # Only right click if we haven't placed all bomb guesses
                    # or the square is already flagged
                    right_conditions = not s.is_clicked and \
                                       (s.is_flagged or self.numGuesses() > 0)

                    if event.button == BUTTON_LEFT and left_conditions:
                        # Check if the click triggers a bomb
                        if s.leftClick(self.display, self.theme):
                            playing = self.lose()
                            break
                        # Check if there are zeroes that can be exposed
                        zeroes = []
                        self.findZeroes(s, zeroes)
                        for square in zeroes:
                            square.leftClick(self.display, self.theme)
                    elif event.button == BUTTON_RIGHT and right_conditions:
                        # Perform right click
                        s.rightClick(self.display, self.theme)
                    elif event.button == BUTTON_MIDDLE and s.is_clicked:
                        no_bombs = True
                        # Get all the surrounding squares
                        adj_squares = self.getAdjacent(s)
                        # If one is a bomb and not flagged, stop the clicking
                        if True in [(s.is_bomb and not s.is_flagged) for s in adj_squares]:
                            continue
                        for square in adj_squares:
                            # If the square isn't clicked or flagged, automatically click it
                            if not (square.is_clicked or square.is_flagged):
                                square.leftClick(self.display, self.theme)
                                zeroes = []
                                self.findZeroes(square, zeroes)
                                for square1 in zeroes:
                                    square1.leftClick(self.display, self.theme)
                    self.first = False
                # Check if we won
                if not self.first and self.haveWon():
                    self.setFace(True)
                    playing = False
                    break
            # We exited
            elif event.type == QUIT:
                pygame.quit()
                sys.exit()
        # Update bomb counter and timer
        if not self.first:
            self.play_time += dt / 1000
            self.timer.displayText(secsToString(self.play_time), self.display)
            self.bomb_counter.displayText(str(self.numGuesses()), self.display)
        return playing

    # Checks or restart, true if playing, false if not
    def restart(self, events):
        for event in events:
            if event.type == MOUSEBUTTONUP and event.button == BUTTON_LEFT:
                pos = pygame.mouse.get_pos()
                if self.face.collidepoint(pos):
                    # Reset all squares
                    for row in self.squares:
                        for s in row:
                            s.reset()
                            s.draw(self.display, self.theme)
                    self.setFace(None)
                    self.first = True
                    return True
            elif event.type == QUIT:
                pygame.quit()
                sys.exit()
        return False

    # Helper functions
    # Returns coordinates of bombs, generated randomly
    def setBombs(self, num_rows, num_cols, click_point):
        # Generate bomb locations
        num_squares = num_cols * num_rows
        num_bombs = int(num_squares / 4)
        bomb_coords = []
        for i in range(num_bombs):
            coord = randCoord(0, 0, num_cols, num_rows)
            # Find a new location and add it to our list
            while coord in bomb_coords or coord == click_point:
                coord = randCoord(0, 0, num_cols, num_rows)
            bomb_coords.append(coord)

        for row in self.squares:
            for square in row:
                if square.coord in bomb_coords:
                    square.is_bomb = True
                else:
                    bomb_count = 0
                    for s in self.getAdjacent(square):
                        if s.coord in bomb_coords:
                            bomb_count += 1
                    square.val = bomb_count

    def setTheme(self, theme):
        self.theme = theme
        # Update text views
        self.bomb_counter.setFont(theme.font_name)
        self.timer.setFont(theme.font_name)
        # Update all squares
        for row in self.squares:
            for square in row:
                square.draw(self.display, theme)

    # Sets up the squares
    # Updates squares (global 2D list)
    def setUpSquares(self, width):
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
                                     width, width), (x, y))
                square.draw(self.display, self.theme)
                row.append(square)
            self.squares.append(row)

    # Returns the number of guesses available to the player
    def numGuesses(self):
        num_bombs = 0
        for row in self.squares:
            for s in row:
                # Minus one guess for each flag used
                if s.is_flagged:
                    num_bombs -= 1
                # Plus one guess for each bomb
                if s.is_bomb:
                    num_bombs += 1
        return num_bombs

    # Recursive function that reveals any zeroes near the selected square
    # Also reveals all squares outside those zeroes (So the player doesn't have to)
    # Updates zero_coords list (saves results accross recursion)
    def findZeroes(self, s, zeroes):
        new_squares = []
        for square in self.getAdjacent(s):
            if square not in zeroes and not square.is_clicked \
                    and (square.val is 0 or s.val is 0):
                zeroes.append(square)
                new_squares.append(square)

        for square1 in new_squares:
            if square1.val == 0:
                self.findZeroes(square1, zeroes)

    # Returns list of adjacent squares
    def getAdjacent(self, square):
        result = []
        # Go through every square around the square at x,y
        x = square.coord[0]
        y = square.coord[1]
        for y1 in range(y - 1, y + 2):
            for x1 in range(x - 1, x + 2):
                # Check if the coordinate is valid
                if 0 <= y1 < len(self.squares) and 0 <= x1 < len(self.squares[0]):
                    # Add the square at [y1][x1]
                    result.append(self.squares[y1][x1])
        return result

    # Called when the player loses
    def lose(self):
        # Set face to red
        self.setFace(False)
        # Show all unclicked bombs
        for row in self.squares:
            for s in row:
                if s.is_bomb and not s.is_clicked:
                    s.reveal(self.display, self.theme)
        return False

    # Checks if we have won, returns True if player has won, False otherwise
    def haveWon(self):
        all_flagged = True
        all_clicked = True
        for row in self.squares:
            for s in row:
                # If a square should or shouldn't be flagged then not all the bombs are flagged
                if s.is_bomb != s.is_flagged:
                    all_flagged = False
                # If a square should be clicked then not all non-bombs are clicked
                if not s.is_clicked and not s.is_bomb:
                    all_clicked = False
                # Once both statements are proven false, return false
                if not (all_clicked or all_flagged):
                    return False
        return True

    # Sets face, won = True for won, False for lost, None for playing
    def setFace(self, won):
        face_str = "meh" if won == None else "happy" if won else "sad"
        self.display.blit(getImg(face_str + ".png", (self.face.width, self.face.height)),
                          (self.face.left, self.face.top))


# General Functions
# Generates a random coord with minX <= x < maxX and minY <= y < maxY
def randCoord(minX, minY, maxX, maxY):
    return (randint(minX, maxX - 1), randint(minY, maxY - 1))


# Converts a number of seconds into a string
# Returns a the time as a string in the format hh...:mm:ss
def secsToString(num_secs):
    secs = int(num_secs % 60)
    secs_filler = ":" if secs >= 10 else ":0"
    mins = int((num_secs / 60) % 60)
    mins_filler = ":" if mins >= 10 else ":0"
    hours = int(num_secs / 3600)
    return str(hours) + mins_filler + str(mins) + secs_filler + str(secs)
