from picamera2 import Picamera2
import mediapipe as mp
import cv2


class Interaction:
    def __init__(self) -> None:
        self.mp_drawing = mp.solutions.drawing_utils  # type: ignore
        self.picam2 = Picamera2()
        self.picam2.configure(
            self.picam2.create_preview_configuration(main={"size": (640, 480)}, lores={"size": (320, 240), "format": "YUV420"})  # type: ignore
        )
        self.picam2.start()
        self.hands = mp.solutions.hands.Hands(  # type: ignore
            min_detection_confidence=0.8,
            min_tracking_confidence=0.5,
            static_image_mode=False,
        )

        self.clicking = False

    def register_cursor_render_callback(self, callback):
        self.cursor_render_callback = callback

    def register_click_callback(self, callback):
        self.click_callback = callback

    def tick(self):
        frame = self.picam2.capture_array("lores")
        frame = cv2.flip(frame, 1)  # type: ignore
        image = cv2.cvtColor(frame, cv2.COLOR_YUV420p2BGR)
        detected_image = self.hands.process(image)

        if detected_image.multi_hand_landmarks:
            for hand_lms in detected_image.multi_hand_landmarks:
                thumb_landmark = hand_lms.landmark[4]
                pointer_landmark = hand_lms.landmark[8]

                self.cursor_render_callback(1-thumb_landmark.x, 1-thumb_landmark.y)

                if (thumb_landmark.x - pointer_landmark.x) ** 2 + (
                    thumb_landmark.y - pointer_landmark.y
                ) ** 2 < 0.01 and self.click_callback:
                    if self.clicking == False:
                        self.click_callback(1-thumb_landmark.x, 1-thumb_landmark.y)
                        #print(thumb_landmark.x, thumb_landmark.y)
                    self.clicking = True
                else:
                    self.clicking = False
