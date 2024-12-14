import utils.pigame, pygame
from pygame.locals import *
import os
import RPi.GPIO as GPIO
import time
from time import sleep

os.putenv("SDL_VIDEODRV", "fbcon")
# os.putenv('SDL_FBDEV', '/dev/fb1')
os.putenv("SDL_MOUSEDRV", "dummy")
os.putenv("SDL_MOUSEDEV", "/dev/null")
os.putenv("DISPLAY", "")


class pitft:
    def __init__(self) -> None:
        pygame.init()
        self.pitft = pigame.PiTft()
        self.lcd = pygame.display.set_mode((320, 240))
        self.lcd.fill((0, 0, 0))
        pygame.display.update()

        self.font_small = pygame.font.Font(None, 20)

        GPIO.setmode(GPIO.BCM)
        self.buttons = [22, 17, 27, 23]

        for pin in self.buttons:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def get_button(self, index: int) -> bool:
        return not GPIO.input(self.buttons[index])

    def register_mouse_down_callback(self, callback):
        self.mouse_down_callback = callback

    def register_mouse_up_callback(self, callback):
        self.mouse_up_callback = callback

    def handle_event(self, event):
        if event.type is MOUSEBUTTONDOWN:
            self.mouse_down_callback(pygame.mouse.get_pos())
        if event.type is MOUSEBUTTONUP:
            self.mouse_up_callback(pygame.mouse.get_pos())

    def tick(self):
        self.pitft.update()
        for event in pygame.event.get():
            self.handle_event(event)
