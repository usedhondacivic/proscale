SCREEN_SIZE = (240, 320)

from pitft_helpers import pygame

import numpy as np
from enum import Enum


class GUIStates(Enum):
    HOME = 1
    RECIPE_HOME = 2
    RECIPE_DETAILS = 3


class GUI:
    def __init__(self) -> None:
        self.gui_items = []

        self.state = GUIStates.HOME
        self.state_info = None

        self.cursor_pos = np.array([0.0, 0.0])
        self.cursor_target = np.array([0.0, 0.0])
        self.clicking = False

    def tick(self, surface):
        pygame.draw.rect(surface, (0, 0, 0), pygame.Rect(0, 0, 240, 320))
        # Draw each item
        for item in self.gui_items:
            item.draw(surface, self.state, self.state_info)

        # Cursor
        self.cursor_pos = self.cursor_pos + (self.cursor_target - self.cursor_pos) * 0.5
        color = (0, 255, 255)
        if self.clicking:
            color = (255, 0, 0)
            self.clicking = False
        pygame.draw.circle(
            surface, color, (int(self.cursor_pos[0]), int(self.cursor_pos[1])), 3
        )

    def click_handler(self, x, y):
        self.clicking = True
        # Call each elements click handler
        for item in self.gui_items:
            result = item.check_click(
                (x * SCREEN_SIZE[0], y * SCREEN_SIZE[1]), self.state, self.state_info
            )
            if result is not None:
                (self.state, self.state_info) = result

    def cursor_pos_handler(self, x, y):
        self.cursor_target = np.array([x * SCREEN_SIZE[0], y * SCREEN_SIZE[1]])

    # Each GUI item must implement:
    # draw(self, surface, state: GUIState, state_info) -> None
    # check_click(self, position: Tuple(x, y), state: GUIState, state_info) -> (State, state_info)
    def add_gui_element(self, gui_element):
        self.gui_items.append(gui_element)
