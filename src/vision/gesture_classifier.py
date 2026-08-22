import math


# ============================================================
# DIRECTION FROM TWO POINTS
# ============================================================

def get_direction(wrist, tip):

    dx = tip.x - wrist.x
    dy = tip.y - wrist.y

    magnitude = math.hypot(dx, dy)

    if magnitude < 0.12:
        return "UNKNOWN"

    # Dominant axis determines direction

    if abs(dx) > abs(dy):

        if dx < 0:
            return "LEFT"

        return "RIGHT"

    else:

        if dy < 0:
            return "FORWARD"

        return "BACKWARD"


# ============================================================
# FINGER EXTENSION
# ============================================================

def finger_extended(landmarks, tip, pip):

    return landmarks[tip].y < landmarks[pip].y


# ============================================================
# GESTURE CLASSIFIER
# ============================================================

def classify_gesture(landmarks):

    wrist = landmarks[0]


    # --------------------------------------------------------
    # Finger states
    # --------------------------------------------------------

    index = finger_extended(
        landmarks,
        8,
        6
    )

    middle = finger_extended(
        landmarks,
        12,
        10
    )

    ring = finger_extended(
        landmarks,
        16,
        14
    )

    pinky = finger_extended(
        landmarks,
        20,
        18
    )


    # ========================================================
    # OPEN PALM
    # ========================================================

    if (
        index
        and
        middle
        and
        ring
        and
        pinky
    ):

        return "STOP"


    # ========================================================
    # THUMB DIRECTION
    # ========================================================

    thumb_tip = landmarks[4]

    thumb_direction = get_direction(
        wrist,
        thumb_tip
    )


    # Thumb gesture = other fingers folded

    fingers_folded = (
        not index
        and
        not middle
        and
        not ring
        and
        not pinky
    )


    if fingers_folded:

        if thumb_direction != "UNKNOWN":

            return thumb_direction


    # ========================================================
    # INDEX-FINGER DIRECTION
    # ========================================================

    if index:

        index_tip = landmarks[8]

        index_direction = get_direction(
            wrist,
            index_tip
        )

        if index_direction != "UNKNOWN":

            return index_direction


    # ========================================================
    # UNKNOWN
    # ========================================================

    return "UNKNOWN"