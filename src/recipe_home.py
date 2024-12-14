from __future__ import annotations

from pathlib import Path
import json
import os

import glob

from typing import Tuple, Any

import RPi.GPIO as GPIO
from hx711v0_5_1 import HX711

from pitft_helpers import pygame
from gui import GUIStates

# Get the directory of the current script
script_dir = Path(__file__).parent


class RecipeHome:
    def __init__(self):
        self.large_font = pygame.font.Font(None, 60)
        self.menu_font = pygame.font.Font(None, 20)

        self.recipe_data_paths = glob.glob(str(script_dir / "recipes" / "**/*.json"))
        self.recipe_index = 0

    def draw(self, surface, state: GUIStates, state_info):
        if state is not GUIStates.RECIPE_HOME:
            return

        # Home button
        pygame.draw.rect(surface, (255, 255, 255), pygame.Rect(0, 0, 240, 80), 2)
        text_surface = self.menu_font.render(f"Home", True, (255, 255, 255))
        rect = text_surface.get_rect(center=(120, 40))
        surface.blit(text_surface, rect)

        # Previous button
        pygame.draw.rect(surface, (255, 255, 255), pygame.Rect(0, 80, 120, 80), 2)
        text_surface = self.menu_font.render(f"<<<", True, (255, 255, 255))
        rect = text_surface.get_rect(center=(40, 120))
        surface.blit(text_surface, rect)

        # Next button
        pygame.draw.rect(surface, (255, 255, 255), pygame.Rect(120, 80, 120, 80), 2)
        text_surface = self.menu_font.render(f">>>", True, (255, 255, 255))
        rect = text_surface.get_rect(center=(200, 120))
        surface.blit(text_surface, rect)

        # Image
        with open(
            str(
                self.recipe_data_paths[self.recipe_index % len(self.recipe_data_paths)]
            ),
            "r",
        ) as file:
            recp_data = json.load(file)
            image_rel_path = recp_data["image"]
            image_path = (
                Path(
                    self.recipe_data_paths[
                        self.recipe_index % len(self.recipe_data_paths)
                    ]
                ).parent
                / image_rel_path
            )

            img = pygame.image.load(str(image_path)).convert()
            img = pygame.transform.rotozoom(img, 0, 150 / img.get_height())
            surface.blit(img, (120 - img.get_width() / 2.0, 170))

    def check_click(
        self, pos, state: GUIStates, state_info
    ) -> Tuple[GUIStates, Any] | None:
        if state is GUIStates.RECIPE_HOME:
            if pos[1] < 80:
                return (GUIStates.HOME, None)
            elif pos[1] > 160:
                with open(
                    str(
                        self.recipe_data_paths[
                            self.recipe_index % len(self.recipe_data_paths)
                        ]
                    ),
                    "r",
                ) as file:
                    data = json.load(file)
                    print(data)
                    return (GUIStates.RECIPE_DETAILS, (data, 0))
            elif pos[0] < 120:
                # go to previous recipe
                self.recipe_index -= 1
            elif pos[0] > 120:
                # go to next recipe
                self.recipe_index += 1

        return None
