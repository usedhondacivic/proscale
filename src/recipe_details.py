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

    def draw(self, surface, state: GUIStates, state_info):
        if state is not GUIStates.RECIPE_DETAILS:
            return

        (info, step) = state_info
        # Home button
        pygame.draw.rect(surface, (255, 255, 255), pygame.Rect(0, 0, 240, 80), 2)
        text_surface = self.menu_font.render(f"Home", True, (255, 255, 255))
        rect = text_surface.get_rect(center=(120, 40))
        surface.blit(text_surface, rect)

        # Text
        current_step = info["steps"][step % len(info["steps"])]
        lines = current_step.split("\n")
        y_offset = 180
        for line in lines:
            text_surface = self.menu_font.render(line, True, (255, 255, 255))
            rect = text_surface.get_rect(center=(120, y_offset))
            surface.blit(text_surface, rect)
            y_offset += 20

        # Previous button
        text_surface = self.menu_font.render(f"<<<", True, (255, 255, 255))
        rect = text_surface.get_rect(center=(40, 120))
        surface.blit(text_surface, rect)

        # Next button
        text_surface = self.menu_font.render(f">>>", True, (255, 255, 255))
        rect = text_surface.get_rect(center=(200, 120))
        surface.blit(text_surface, rect)

    def check_click(
        self, pos, state: GUIStates, state_info
    ) -> Tuple[GUIStates, Any] | None:
        if state is GUIStates.RECIPE_DETAILS:
            (info, step) = state_info
            if pos[1] < 80:
                return (GUIStates.HOME, None)
            elif pos[0] < 120:
                return (GUIStates.RECIPE_DETAILS, (info, step - 1))
            elif pos[0] > 120:
                return (GUIStates.RECIPE_DETAILS, (info, step + 1))

        return None
