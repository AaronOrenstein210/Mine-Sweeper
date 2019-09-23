# Created on 9/4/19

import pygame


class TextView:
    def __init__(self, rect):
        self.rect = rect
        self.font_name = "Times New Roman"

    # Displays text onto display
    def displayText(self, text, display):
        pygame.draw.rect(display, (75, 75, 75), self.rect)
        font = getScaledFont(self.rect.w, self.rect.h, text, self.font_name)
        text = font.render(text, 1, (0, 0, 0))
        text_rect = text.get_rect(center=(self.rect.centerx, self.rect.centery))
        display.blit(text, text_rect)

    # Sets font
    def setFont(self, font_name):
        self.font_name = font_name


# Gets the biggest font that fits the text within max_w and max_H
def getScaledFont(max_w, max_h, text, font_name):
    font_size = 0
    font = pygame.font.SysFont(font_name, font_size)
    w, h = font.size(text)
    while w < max_w and h < max_h:
        font_size += 1
        font = pygame.font.SysFont(font_name, font_size)
        w, h = font.size(text)
    return pygame.font.SysFont(font_name, font_size - 1)
