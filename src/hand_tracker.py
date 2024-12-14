from picamera2 import Picamera2
import mediapipe as mp
import cv2


mp_drawing = mp.solutions.drawing_utils  # type: ignore
mp_hands = mp.solutions.hands  # type: ignore
picam2 = Picamera2()
picam2.configure(
    picam2.create_preview_configuration(main={"size": (640, 480)}, lores={"size": (320, 240), "format": "YUV420"}, transform=libcamera.Transform(hflip=1, vflip=1))  # type: ignore
)
picam2.start()

with mp_hands.Hands(static_image_mode=False, min_detection_confidence=0.8, min_tracking_confidence=0.8, max_num_hands=1) as hands:
    while True:
        frame = picam2.capture_array("lores")
        #frame = cv2.flip(frame, 1)  # type: ignore
        #frame = cv2.rotate(frame, cv2.ROTATE_180)
        image = cv2.cvtColor(frame, cv2.COLOR_YUV420p2BGR)
        #height, width,_ = image.shape
        #image = cv2.rotate(image, cv2.ROTATE_180)
        detected_image = hands.process(image)
        # image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        image = cv2.resize(image, (320, 240))

        if detected_image.multi_hand_landmarks:
            for hand_lms in detected_image.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image,
                    hand_lms,
                    mp_hands.HAND_CONNECTIONS,
                    landmark_drawing_spec=mp.solutions.drawing_utils.DrawingSpec(  # type: ignore
                        color=(255, 0, 255), thickness=4, circle_radius=2
                    ),
                    connection_drawing_spec=mp.solutions.drawing_utils.DrawingSpec(  # type: ignore
                        color=(20, 180, 90), thickness=2, circle_radius=2
                    ),
                )
                thumb_landmark = hand_lms.landmark[4]
                pointer_landmark = hand_lms.landmark[8]

                color = (255, 0, 0)
                if (thumb_landmark.x - pointer_landmark.x) ** 2 + (
                    thumb_landmark.y - pointer_landmark.y
                ) ** 2 < 0.01:
                    color = (0, 255, 0)

                cv2.circle(
                    image,
                    (int(pointer_landmark.x * 320), int(pointer_landmark.y * 240)),
                    10,
                    color,
                    5,
                )

        image = cv2.cvtColor(image, cv2.COLOR_BGR2BGR565)
        with open("/dev/fb0", "rb+") as buf:
            buf.write(image)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cv2.destroyAllWindows()
