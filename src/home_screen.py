from __future__ import annotations

from typing import Tuple, Any

import RPi.GPIO as GPIO
from hx711v0_5_1 import HX711

from pitft_helpers import pygame
from gui import GUIStates
import numpy as np

class HomeScreen:
    def __init__(self):
        button_pins = [22, 27, 17, 23]
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        for pin in button_pins:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        ReferenceUnit = 384
        self.hx = HX711(5, 6)
        self.hx.setReferenceUnit(ReferenceUnit)
        self.hx.tare()
        self.hx.setUnit("gram")
        self.hx.reset()

        self.reading = 0.0

        self.large_font = pygame.font.Font(None, 60)
        self.menu_font = pygame.font.Font(None, 20)
        print("Scale intialized!")

    def draw(self, surface, state: GUIStates, state_info):
        if state is not GUIStates.HOME:
            return

        # Show weight
        weight = self.hx.getWeight()
        buffer = []
        buffer.append(weight)
        if len(buffer) > 10:
            buffer.pop(0)
        current_weight = np.median(buffer)

        difference = abs(abs(current_weight) - abs(self.reading))
        if 1 < difference < 500:
            self.reading = current_weight

        text_surface = self.large_font.render(
            f"{round(self.reading)}", True, (255, 255, 255)
        )
        rect = text_surface.get_rect(center=(120, 210))
        surface.blit(text_surface, rect)
        text_surface = self.large_font.render(
            f"{self.hx.getUnit()}s", True, (255, 255, 255)
        )
        rect = text_surface.get_rect(center=(120, 275))
        surface.blit(text_surface, rect)

        # Tare button
        pygame.draw.rect(surface, (255, 255, 255), pygame.Rect(0, 0, 120, 80), 2)
        text_surface = self.menu_font.render(f"Tare", True, (255, 255, 255))
        rect = text_surface.get_rect(center=(60, 40))
        surface.blit(text_surface, rect)

        # Units button
        pygame.draw.rect(surface, (255, 255, 255), pygame.Rect(120, 0, 120, 80), 2)
        text_surface = self.menu_font.render(f"Unit", True, (255, 255, 255))
        rect = text_surface.get_rect(center=(180, 40))
        surface.blit(text_surface, rect)

        # Recipes button
        pygame.draw.rect(surface, (255, 255, 255), pygame.Rect(0, 80, 240, 80), 2)
        text_surface = self.menu_font.render(f"Recipes", True, (255, 255, 255))
        rect = text_surface.get_rect(center=(120, 120))
        surface.blit(text_surface, rect)

    def check_click(
        self, pos, state: GUIStates, state_info
    ) -> Tuple[GUIStates, Any] | None:
        if state is GUIStates.HOME:
            if pos[0] < 120 and pos[1] < 80:
                self.hx.tare()

            if pos[0] > 120 and pos[1] < 80:
                if self.hx.getUnit() == "gram":
                    self.hx.setUnit("ounce")
                else:
                    self.hx.setUnit("gram")

            if pos[1] > 80 and pos[1] < 160:
                return (GUIStates.RECIPE_HOME, None)

        return None
