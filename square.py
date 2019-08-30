# Created on 8/27/2019

import pygame


class Square:
    def __init__(self, rect, is_bomb):
        self.boundary = rect
        self.inside = rect.inflate(-(rect.width / 20), -(rect.height / 20))
        self.is_bomb = is_bomb
        self.is_flagged = False
        self.is_clicked = False
        self.val = -1

    def draw(self, display):
        pygame.draw.rect(display, (0, 0, 0), self.boundary)
        pygame.draw.rect(display, (128, 128, 128), self.inside)

    def onClick(self, display, left, font):
        color = (0, 0, 0)
        if left:
            # It wasn't a bomb, reveal its number
            if not self.is_bomb:
                color = (200, 200, 200)
            # It was a bomb and wasn't flagged, game over
            elif not self.is_flagged:
                color = (255, 0, 0)
            # No change
            else:
                color = (0, 0, 255)
            self.is_clicked = True
        # Toggle if it is flagged or not
        else:
            color = (0, 0, 255) if not self.is_flagged else (128, 128, 128)
            self.is_flagged = not self.is_flagged
        # Change the color
        pygame.draw.rect(display, color, self.inside)
        # Reveal the number if successfully left clicked
        if color is (200, 200, 200):
            text = font.render(str(self.val), 1, (0, 0, 0))
            text_rect = text.get_rect(center=(self.inside.centerx, self.inside.centery))
            display.blit(text, text_rect)
        # Return if we activated a bomb or not
        return color is (255, 0, 0)
