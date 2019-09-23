# Created on 8/27/2019

import pygame


class Square:
    def __init__(self, rect, coord):
        self.inside = rect.inflate(-(rect.width / 20), -(rect.height / 20))
        self.is_bomb = False
        self.is_flagged = False
        self.is_clicked = False
        self.val = -1
        self.coord = coord

    def reset(self):
        self.is_bomb = False
        self.is_flagged = False
        self.is_clicked = False
        self.val = -1

    def draw(self, display, theme):
        # Flagged = blue, bomb (not flagged) = red, clicked (number) = light grey,
        # default = grey
        color = (0, 0, 255) if self.is_flagged else (128, 128, 128) if not self.is_clicked \
            else (255, 0, 0) if self.is_bomb else (200, 200, 200)
        pygame.draw.rect(display, color, self.inside)
        # Figure out foreground images
        if self.is_flagged or (self.is_bomb and self.is_clicked):
            img = theme.flag_img if self.is_flagged else theme.bomb_img
            display.blit(getImg(img, (self.inside.width, self.inside.height)),
                         (self.inside.left, self.inside.top))
        elif self.is_clicked:
            color = (0, 0, 128) if self.val == 1 else (0, 128, 0) if self.val == 2 \
                else (128, 0, 0) if self.val == 3 else (128, 0, 128) if self.val == 4 \
                else (200, 0, 128) if self.val == 5 else (0, 100, 128) if self.val == 6 \
                else (10, 0, 10) if self.val == 7 else (200, 200, 200)
            text = theme.font.render(str(self.val), 1, color)
            text_rect = text.get_rect(center=(self.inside.centerx, self.inside.centery))
            display.blit(text, text_rect)

    def reveal(self, display, theme):
        if self.is_bomb:
            pygame.draw.rect(display, (255, 0, 0), self.inside)
            img = theme.flag_img if self.is_flagged else theme.bomb_img
            display.blit(getImg(img, (self.inside.width, self.inside.height)),
                         (self.inside.left, self.inside.top))

    # Perform left click
    def leftClick(self, display, theme):
        self.is_clicked = True

        self.draw(display, theme)

        if self.is_bomb:
            pygame.mixer.music.load("bomb_sound.mp3")
            pygame.mixer.music.play()

        # Return true if we clicked a bomb
        return self.is_bomb

    # Perform right click
    def rightClick(self, display, theme):
        self.is_flagged = not self.is_flagged

        self.draw(display, theme)


# Return scaled img
def getImg(name, dim):
    img = pygame.image.load(name)
    return pygame.transform.scale(img, dim)
