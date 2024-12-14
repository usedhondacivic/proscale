# Some useful standard libs
from time import sleep
import threading

# API for the pitft
from pitft_helpers import pitft, pygame

# Handler for picamera / mediapipe interaction
from interaction import Interaction

# Pages
from home_screen import HomeScreen
from recipe_home import RecipeHome
from recipe_details_weight import RecipeDetails

# GUI
from gui import GUI

# Initialize peripheral drivers
tft = pitft()
interface = Interaction()
gui = GUI()

#tft.register_mouse_down_callback(gui.click_handler)
gui.add_gui_element(HomeScreen())
gui.add_gui_element(RecipeHome())
gui.add_gui_element(RecipeDetails())

# Interaction callbacks
interface.register_cursor_render_callback(gui.cursor_pos_handler)
interface.register_click_callback(gui.click_handler)


# Threads
def interaction_thread():
    while True:
        interface.tick()


def rendering_thread():
    while True:
        tft.tick()
        gui.tick(tft.lcd)
        pygame.display.update()
        sleep(1.0 / 30.0)


thread_i = threading.Thread(target=interaction_thread, daemon=True)
thread_i.start()
thread_r = threading.Thread(target=rendering_thread, daemon=True)
thread_r.start()

# Loop and wait for exit signal
try:
    while True:
        pass
except KeyboardInterrupt:
    pass

# Clean up tft gracefully
del tft.pitft

# Both threads are marked as daemon - they'll exit as soon as the main program does
