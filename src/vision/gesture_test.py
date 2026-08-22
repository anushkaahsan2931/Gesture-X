import cv2
import mediapipe as mp

from src.vision.gesture_controller import gesture_to_command


# ============================================================
# MEDIAPIPE
# ============================================================

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils


hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)


# ============================================================
# CAMERA
# ============================================================

camera = cv2.VideoCapture(0)

if not camera.isOpened():

    print("ERROR: Camera could not open.")

    hands.close()

    exit()


print()
print("================================")
print("GESTURE-X DIRECTION TEST")
print("================================")
print()
print("UP       = FORWARD")
print("DOWN     = BACKWARD")
print("LEFT     = LEFT")
print("RIGHT    = RIGHT")
print("FIST     = STOP")
print("OPEN PALM = STOP")
print()
print("Press Q to quit.")
print()


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    success, frame = camera.read()

    if not success:
        break


    # Mirror camera

    frame = cv2.flip(
        frame,
        1
    )


    # Convert to RGB

    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )


    # Detect hand

    results = hands.process(
        rgb
    )


    command = "IDLE"


    # ========================================================
    # HAND
    # ========================================================

    if results.multi_hand_landmarks:

        hand = results.multi_hand_landmarks[0]


        # Draw hand

        mp_draw.draw_landmarks(

            frame,

            hand,

            mp_hands.HAND_CONNECTIONS

        )


        # Classify

        command = gesture_to_command(

            hand.landmark

        )


    # ========================================================
    # DISPLAY
    # ========================================================

    cv2.putText(

        frame,

        f"COMMAND: {command}",

        (20, 50),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.9,

        (0, 255, 255),

        2

    )


    cv2.putText(

        frame,

        "UP = FORWARD",

        (20, 100),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.55,

        (255, 255, 255),

        1

    )


    cv2.putText(

        frame,

        "DOWN = BACKWARD",

        (20, 130),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.55,

        (255, 255, 255),

        1

    )


    cv2.putText(

        frame,

        "LEFT / RIGHT = TURN",

        (20, 160),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.55,

        (255, 255, 255),

        1

    )


    cv2.putText(

        frame,

        "FIST / PALM = STOP",

        (20, 190),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.55,

        (255, 255, 255),

        1

    )


    cv2.putText(

        frame,

        "Q = EXIT",

        (20, 230),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.55,

        (255, 255, 255),

        1

    )


    cv2.imshow(

        "Gesture-X | Direction Test",

        frame

    )


    # ========================================================
    # QUIT
    # ========================================================

    if cv2.waitKey(1) & 0xFF == ord("q"):

        break


# ============================================================
# CLEANUP
# ============================================================

camera.release()

cv2.destroyAllWindows()

hands.close()