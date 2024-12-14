# ProScale - A Smart, Gesture Controlled, Contact Free Kitchen Scale

*By Michael Crum (mmc323@cornell.edu) and Zehui Lin (zl883)*

![Banner](./assets/banner.png)

## Objective

In our final project, we developed a kitchen scale with gesture-based controls, utilizing a Raspberry Pi, a load cell with an HX711 sensor, and a piTFT display. 
Motivated by the challenges of maintaining hygiene in the kitchen, we set out to create a hands-free solution that also enhances accessibility for individuals with limited mobility.
Users can easily weigh ingredients, switch units, and navigate recipes through a gesture-based interface on the piTFT screen, enhancing the kitchen prep experience.

## Introduction

This project integrates hardware and software to build a gesture-controlled kitchen scale.
At its core, the system utilizes a Raspberry Pi for processing, with a PiCamera for real-time video capture, a load cell with HX711 sensor for weight measurements, and a piTFT display serving as the user interface, all housed in a custom laser-cut case.
The captured video is pre-processed using OpenCV for frame flipping, color conversion, and scaling, followed by MediaPipe for detecting 21 hand landmarks.
By analyzing the positions and distances of these landmarks, gestures like pinching and pointing are identified and mapped to actions like navigating recipes, switching units, and the tare function.
The interface, developed using PyGame, dynamically updates in response to cursor movement and click events, providing a touch-free, hygienic, and accessible user experience.

## High-Level System Design

> Figure 1: High-Level System Design

## Hardware Setup


> Figure2: Final Hardware Setup

## OpenCV and MediaPipe Implementation


> Figure 3: Hand Landmarks

Google MediaPipe is a collection of optimized tools for applying machine learning models for various computer vision tasks.
Of particular interest to us is the hand landmarks model, which identifies hands within an input image and extracts the location of each joint.
See figure todo for a diagram of each landmark output from the algorithm.
Each landmark has a corresponding x and y location in screen space, as well as an estimate of z - the depth of the landmark.

MediaPipe requires video input to process.
We decided to use a picamera because it is widely supported and well documented.
We installed the picamera python driver using sudo apt install -y python3-picamera2, then ran a simple test program to open a preview window:

```python
from picamera2 import Picamera2, Preview
import time
picam2 = Picamera2()
camera_config = picam2.create_still_configuration(main={"size": (1920, 1080)}, lores={"size": (640, 480)}, display="lores")
picam2.configure(camera_config)
picam2.start_preview(Preview.QTGL)
picam2.start()
time.sleep(60)
```

This example requires an X server connection and the QTGL driver to be available.
This is only the case when running the graphical desktop through the RPi’s HDMI port, and doesn’t work over an SSH connection.
To run the example over SSH, it is possible to forward the local X server using `ssh -x`, although the QTGL driver won’t be available. Instead, you’ll need to switch `Preview.QTGL` to `Preview.QT`.

Because our system is intended to run without an external display, we next looked for a way to display the piTFT’s output on the TFT’s screen. QT provides a framebuffer driver, but we were unable to make it function in our testing. Instead, we chose to write directly to the TFT’s frame buffer. This can be achieved as shown in the following snippet:

TODO

With the picam up and running, we installed MediaPipe using `sudo pip install mediapipe` (`sudo` for compatibility with PyGame, which requires root to display on the TFT).
We were able to display an annotated diagram from the hand recognition model using the following snippet:

TODO

## Weight Measurement
The weight measurement module combines the HX711 sensor, the 5kg load cell, and the Raspberry Pi to obtain weight readings.
The hardware configuration began with connecting the HX711's data (DT) and clock (SCK) pins to GPIO 5 and 6, respectively, and connecting three physical buttons on piTFT to GPIO pins 17, 22, and 27 for critical functions such as tare, unit switching, and quit. 
These buttons were added as a convenient and straightforward interface to streamline the testing process.

With the setup complete, we began testing the weight measurement module with the library `clone git@github.com:tatobari/hx711py.git`. 
However, when running the example code, we encountered challenges with obtaining valid weight readings. Despite verifying that the power supply, DT, and SCK pins were functioning correctly using a multimeter, we observed no small voltage changes across the signal wires (A+ and A-) when weight was applied.
Further multimeter diagnostics indicated abnormally low resistance between A+ and A-, indicating a potential fault in the load cell itself.
To address this, we replaced the load cell with a new component.
We then tested the system again, confirmed stable voltage across the signal and excitation wires, and successfully obtained weight measurements.
Then we calibrated the system using a 100g reference weight to further refine the weight measurement process.

Another issue arose due to the time-sensitive nature of polling bits from the HX711 on the Raspberry Pi.
The Raspberry Pi running on the Linux-based operating system may prioritize other tasks over GPIO operations, leading to occasional random or noisy values in the weight readings.
To mitigate this issue, we initially implemented an exponential smoothing method to stabilize the output, which calculates a weighted average of the current reading and the previous smoothed value using the following formula:

Smoothed Value=$\alpha \times$Current Value$+(1−\alpha)\times$Previous Smoothed Value

where α is the smoothing factor. 
However, this approach did not perform as expected, possibly due to the frequent large noise fluctuations, regardless of the choice of α.

We then used a median filter to reduce the effect.
A buffer was used to store the ten most recent readings, and the median of these values was returned as the current weight.
This sliding window approach effectively removed large outliers and provided a relatively consistent measurement.
It also ensured that random fluctuations had less impact while still allowing the system to adapt to real weight changes.

Functional testing verified the proper operation of all core features.
The tare function can reset the weight to zero by taking the current raw reading from the sensor and setting it as the offset.
And the unit toggle enables switching between grams and ounces using the setUnit() function, with the conversion handled in the rawBytesToWeight() function by multiplying the weight in grams by the conversion factor 0.035274 when switched to ounces. 
And the quit button enabled a smooth shutdown with GPIO cleanup.

## Menu Design

### Initial Design

The initial design of the menu was structured around simplicity and intuitive navigation.
It included a Main Menu with two primary options: Scale Mode and Recipe Mode. 
Scale Mode provided real-time weight measurements, as well as unit conversion and tare capability.
Recipe Mode allowed users to browse recipes and follow step-by-step instructions, with navigation buttons for switching between recipes and steps.
Upon completion of a recipe, users were prompted with a feedback screen to like or dislike the recipe.

> Figure 4: Initial Menu Design

### Final Design

In our final design, we chose to incorporate the scale mode directly into the home page and orient the piTFT screen vertically. 
By combining the scale mode with the home screen, users can perform weight measurements, tare, and unit switching without navigating away, streamlining functionality and reducing complexity.
The vertical orientation further improves usability by optimizing the display for button and reading flow, as well as allowing for larger text and images, making it easier to follow instructions and see real-time measurements at a glance.

The Home page is the initial interface displayed upon starting the system, providing access to core scale functions and navigation options.
It prominently shows real-time weight readings from the HX711 sensor at the bottom, which is dynamically updated by the draw() function The top section features buttons for tare and unit switching, which can be activated through gestures detected by the check_click(), triggering respective functions such as self.hx.tare() to reset the scale and self.hx.setUnit() to toggle between grams and ounces. And the Recipes button directs users to the recipe page.

On the Recipe Home page, the bottom area displays an image of the stored recipe, loaded dynamically from json files using pygame.image.load and scaled with pygame.transform.rotozoom. 
The top section includes a Home button, allowing users to return to the home page. And users can cycle through the recipes by “clicking” the “<<<” and ”>>>” buttons. The check_click() function handles navigation by updating the self.recipe_index variable, while the draw function ensures that the image is rendered in real-time. 

The interface on the Recipe Details page combines step-by-step recipe instructions with real-time weight measurements to streamline the cooking process. The topmost part contains the Home and Return buttons that allow users to return to the home page or recipe home page, respectively. Weight measurements with the unit are shown below, along with Tare and Unit buttons, like on the Home page. And the recipe instructions are loaded from json files at the bottom. The instructions are dynamically rendered and are updated when a pinching gesture is detected, which helps users easily progress to the next step without touching the device. Specifically, pinching left moves to the previous step, while pinching right progresses to the next step. By integrating real-time weight measurements with dynamically updated instructions, the Recipe Details page provides an intuitive and efficient user experience.


> Figure 5: Home Page, Recipe Home Page, and Recipe Details Page (from left to right). The blue point indicates the gesture-detected cursor.

### Integration

After designing the individual pages, we wrote gui.py to tie together the menu components, ensuring smooth transitions and interactions across screens.
It utilizes the GUIStates enum to manage the screens and switches between them dynamically.
The tick() function redraws the screen and updates the cursor position based on gesture inputs. Gesture-based interaction is facilitated by the cursor_pos_handler() and click_handler, which handle cursor movement and click events triggered by MediaPipe-detected gestures.
Each screen is registered as a GUI element through the add_gui_element() function, creating a modular structure that supports future scalability.
This integrated design ensures a simple and easy-to-use user experience across the entire interface.

Finally, app.py was implemented to integrate all components, connecting the GUI, gesture recognition, and hardware functionalities. 
The script first initializes the piTFT display, the Interaction module for gesture processing, and the GUI object.
Interaction callbacks bring gesture inputs to the GUI, with cursor_pos_handler() updating the cursor position and click_handler() performing page-specific actions.
To ensure smooth operation, app.py makes use of multithreading, with one thread processing gesture inputs in real-time and another updating the piTFT display at 30 frames per second using the tick() function.
By combining these aspects, app.py provides rapid screen transitions and cohesive interaction across all components, giving a scalable, efficient, and intuitive user experience.

## Results

Overall, we’ve achieved the goals outlined in the description and delivered a functional prototype that integrated gesture-based controls, weight measurement, and recipe navigation.
Core functionalities were all successfully implemented and tested. Gesture detection powered by Picamera and MediaPipe successfully identified hand gestures such as pinching and pointing, enabling precise and intuitive interactions.
The weighting function, driven by the HX711 sensor and a 5kg load cell, provided accurate and stable weight readings after resolving initial hardware issues and implementing a robust median filter.
The GUI design, which includes a home page, a recipe home page, and a recipe details page, simplifies users' prep experience while ensuring hygiene and accessibility, with the piTFT seamlessly updating the interface in real time.

## Conclusion





Future Work
TODO (if any)
We would also integrate a microcontroller to handle the precise bit-polling required by the HX711 sensor, reducing the impact of the Raspberry Pi's multitasking on measurement reliability. We would also have provided a feedback page at the end of each recipe, allowing users to like or dislike recipes, as well as the ability to customize ingredient quantities to suit their preferences or serving sizes.




Budget
Raspberry Pi 4 & piTFT - Provided in the lab
Raspberry Pi Camera - Provided in the lab
5kg Load Cell & HX711 Weight Sensor - $6
Contribution


Code Appendix


Reference
Software
MediaPipe
https://pypi.org/project/mediapipe-rpi4/
https://mediapipe.readthedocs.io/en/latest/solutions/hands.html


OpenCV
https://raspberrypi-guide.github.io/programming/install-opencv
https://opencv.org/


HX711
https://github.com/tatobari/hx711py/tree/master

Hardware
PiCamera
https://picamera.readthedocs.io/en/release-1.13/index.html
https://projects.raspberrypi.org/en/projects/getting-started-with-picamera


HX711 sensor & Load Cell
https://tutorials-raspberrypi.com/digital-raspberry-pi-scale-weight-sensor-hx711/#google_vignette

Past Student Project
Gesture Home
https://courses.ece.cornell.edu/ece5990/ECE5725_Fall2023_Projects/4%20Friday%20December%208/5%20Gesture%20Home%20/GestureHome_web/index.html


