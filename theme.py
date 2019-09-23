# Created on 9/10/2019

from pygame import font
from textView import getScaledFont


class Theme:
    def __init__(self, bomb_img, flag_img, font_name, width):
        self.bomb_img = bomb_img
        self.flag_img = flag_img
        self.font_name = font_name
        self.font = getScaledFont(width * 19 / 20, width * 19 / 20, "0", font_name)
