from __future__ import annotations

from typing import Tuple, Any

import RPi.GPIO as GPIO
from hx711v0_5_1 import HX711

from pitft_helpers import pygame
from gui import GUIStates


class RecipeDetails:
    def __init__(self):
        self.large_font = pygame.font.Font(None, 60)
        self.menu_font = pygame.font.Font(None, 20)
        self.content_font = pygame.font.Font(None, 14)
        ReferenceUnit = 384
        self.hx = HX711(5, 6)
        self.hx.setReferenceUnit(ReferenceUnit)
        self.hx.tare()
        self.hx.setUnit("gram")
        self.hx.reset()

        self.reading = 0.0

        self.large_font = pygame.font.Font(None, 60)
        self.weight_font = pygame.font.Font(None, 40)
        self.menu_font = pygame.font.Font(None, 20)
        print("Scale intialized!")

    def draw(self, surface, state: GUIStates, state_info):
        if state is not GUIStates.RECIPE_DETAILS:
            return

        (info, step) = state_info
        # Home button
        pygame.draw.rect(
            surface, (255, 255, 255), pygame.Rect(
        0, 0, 120, 60), 2)
        text_surface = self.menu_font.render(f"Home", True, (255, 255, 255))
        rect = text_surface.get_rect(center=(60, 30))
        surface.blit(text_surface, rect)

        # Return button
        pygame.draw.rect(
            surface, (255, 255, 255), pygame.Rect(
        120, 0, 120, 60), 2)
        text_surface = self.menu_font.render(f"Return", True, (255, 255, 255))
        rect = text_surface.get_rect(center=(180, 30))
        surface.blit(text_surface, rect)

        # Tare button
        pygame.draw.rect(surface, (255, 255, 255), pygame.Rect(0, 60, 120, 60), 2)
        text_surface = self.menu_font.render(f"Tare", True, (255, 255, 255))
        rect = text_surface.get_rect(center=(60, 90))
        surface.blit(text_surface, rect)

        # Units button
        pygame.draw.rect(surface, (255, 255, 255), pygame.Rect(120, 60, 120, 60), 2)
        text_surface = self.menu_font.render(f"Unit", True, (255, 255, 255))
        rect = text_surface.get_rect(center=(180, 90))
        surface.blit(text_surface, rect)

        # Text
        stp = step % len(info["steps"])
        if stp < 0:
            stp = 0
        current_step = info["steps"][stp]
        lines = current_step.split("\n")
        y_offset = 180
        for line in lines:
            text_surface = self.menu_font.render(line, True, (255, 255, 255))
            rect = text_surface.get_rect(center=(120, y_offset))
            surface.blit(text_surface, rect)
            y_offset += 20

        # Show weight
        weight = self.hx.getWeight()
        difference = abs(abs(weight) - abs(self.reading))
        if 1 < difference < 500 and difference > 0.05 * weight:
            self.reading = weight

        text_surface = self.weight_font.render(
            f"{round(self.reading)}", True, (255, 255, 255)
        )
        rect = text_surface.get_rect(center=(80, 150))
        surface.blit(text_surface, rect)
        text_surface = self.weight_font.render(
            f"{self.hx.getUnit()}s", True, (255, 255, 255)
        )
        rect = text_surface.get_rect(center=(160, 150))
        surface.blit(text_surface, rect)

    def check_click(self, pos, state: GUIStates,
                    state_info) -> Tuple[GUIStates, Any] | None:
        if state is GUIStates.RECIPE_DETAILS:
            (info, step) = state_info
            if pos[1] < 60:
                if pos[0] < 120:
                    return (GUIStates.HOME, None)
                elif pos[0] > 120:
                    return (GUIStates.RECIPE_HOME, None)
            if 60 < pos[1] < 120:
                if pos[0] < 120:
                    self.hx.tare()
                elif pos[0] > 120:
                    if self.hx.getUnit() == "gram":
                        self.hx.setUnit("ounce")
                    else:
                        self.hx.setUnit("gram")
            elif pos[0] < 120:
                return (GUIStates.RECIPE_DETAILS, (info, step - 1))
            elif pos[0] > 120:
                return (GUIStates.RECIPE_DETAILS, (info, step + 1))
        return None
