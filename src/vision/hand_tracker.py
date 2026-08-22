import cv2
import mediapipe as mp

from src.vision.gesture_classifier import classify_gesture


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

    print("ERROR: Could not open camera.")

    hands.close()

    exit()


print("Gesture-X camera started.")
print("Show your hand to the camera.")
print("Press Q to quit.")


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    success, frame = camera.read()

    if not success:

        print("ERROR: Could not read camera.")

        break


    # --------------------------------------------------------
    # Mirror camera
    # --------------------------------------------------------

    frame = cv2.flip(
        frame,
        1
    )


    # --------------------------------------------------------
    # Convert BGR → RGB
    # --------------------------------------------------------

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )


    # --------------------------------------------------------
    # Detect hand
    # --------------------------------------------------------

    results = hands.process(
        rgb_frame
    )


    # ========================================================
    # HAND DETECTED
    # ========================================================

    if results.multi_hand_landmarks:

        for hand_landmarks in results.multi_hand_landmarks:

            # ------------------------------------------------
            # Draw hand skeleton
            # ------------------------------------------------

            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )


            # ------------------------------------------------
            # Classify gesture
            # ------------------------------------------------

            gesture = classify_gesture(
                hand_landmarks.landmark
            )


            # ------------------------------------------------
            # Status
            # ------------------------------------------------

            cv2.putText(

                frame,

                "HAND DETECTED",

                (20, 40),

                cv2.FONT_HERSHEY_SIMPLEX,

                1,

                (0, 255, 0),

                2

            )


            # ------------------------------------------------
            # Gesture
            # ------------------------------------------------

            cv2.putText(

                frame,

                f"GESTURE: {gesture}",

                (20, 90),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.9,

                (255, 255, 0),

                2

            )


            # ------------------------------------------------
            # Index coordinates
            # ------------------------------------------------

            index = hand_landmarks.landmark[8]


            cv2.putText(

                frame,

                f"Index X: {index.x:.2f}",

                (20, 130),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.6,

                (255, 255, 255),

                2

            )


            cv2.putText(

                frame,

                f"Index Y: {index.y:.2f}",

                (20, 160),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.6,

                (255, 255, 255),

                2

            )


    # ========================================================
    # NO HAND
    # ========================================================

    else:

        cv2.putText(

            frame,

            "NO HAND DETECTED",

            (20, 40),

            cv2.FONT_HERSHEY_SIMPLEX,

            1,

            (0, 0, 255),

            2

        )


    # ========================================================
    # DISPLAY
    # ========================================================

    cv2.imshow(

        "Gesture-X | Hand Tracking",

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

print("Gesture-X camera stopped.")