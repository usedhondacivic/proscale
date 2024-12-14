import pygame
import utils.pigame as pigame
from pygame.locals import *
import os
import RPi.GPIO as GPIO
import time
from time import sleep

os.putenv("SDL_VIDEODRV", "fbcon")
os.putenv("SDL_FBDEV", "/dev/fb0")
os.putenv("SDL_MOUSEDRV", "dummy")
os.putenv("SDL_MOUSEDEV", "/dev/null")
os.putenv("DISPLAY", "")


class pitft:
    def __init__(self) -> None:
        pygame.init()
        self.pitft = pigame.PiTft(swapxy=True)
        self.lcd = pygame.display.set_mode((240, 320))
        self.lcd.fill((0, 0, 0))
        pygame.display.update()

        self.font_small = pygame.font.Font(None, 20)
        self.font_large = pygame.font.Font(None, 40)
        self.font_Xlarge = pygame.font.Font(None, 60)
        GPIO.setmode(GPIO.BCM)
        self.buttons = [22, 17, 27, 23]

        for pin in self.buttons:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        #self.mouse_down_callback = None
        #self.mouse_up_callback = None

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
