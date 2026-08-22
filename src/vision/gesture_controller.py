import math


# ============================================================
# DIRECTION
# ============================================================

def get_direction(wrist, tip):

    dx = tip.x - wrist.x
    dy = tip.y - wrist.y

    distance = math.hypot(dx, dy)

    if distance < 0.08:
        return "UNKNOWN"

    angle = math.degrees(
        math.atan2(dx, -dy)
    )

    if angle > 180:
        angle -= 360

    if angle < -180:
        angle += 360


    # FORWARD

    if -40 <= angle <= 40:
        return "FORWARD"


    # RIGHT

    if 40 < angle < 140:
        return "RIGHT"


    # BACKWARD

    if angle >= 140 or angle <= -140:
        return "BACKWARD"


    # LEFT

    if -140 < angle < -40:
        return "LEFT"


    return "UNKNOWN"


# ============================================================
# THUMB DIRECTION
# ============================================================

def get_thumb_direction(landmarks):

    thumb_mcp = landmarks[2]

    thumb_tip = landmarks[4]


    dx = thumb_tip.x - thumb_mcp.x

    dy = thumb_tip.y - thumb_mcp.y


    distance = math.hypot(
        dx,
        dy
    )


    if distance < 0.04:
        return "UNKNOWN"


    angle = math.degrees(
        math.atan2(
            dx,
            -dy
        )
    )


    if angle > 180:
        angle -= 360


    if angle < -180:
        angle += 360


    # ========================================================
    # FORWARD
    # ========================================================

    if -55 <= angle <= 55:
        return "FORWARD"


    # ========================================================
    # RIGHT
    # ========================================================

    if 55 < angle < 125:
        return "RIGHT"


    # ========================================================
    # BACKWARD
    # ========================================================

    if angle >= 125 or angle <= -125:
        return "BACKWARD"


    # ========================================================
    # LEFT
    # ========================================================

    if -125 < angle < -55:
        return "LEFT"


    return "UNKNOWN"


# ============================================================
# FINGER EXTENDED
# ============================================================

def finger_extended(
    landmarks,
    tip,
    pip
):

    tip_distance = math.hypot(

        landmarks[tip].x
        - landmarks[0].x,

        landmarks[tip].y
        - landmarks[0].y

    )


    pip_distance = math.hypot(

        landmarks[pip].x
        - landmarks[0].x,

        landmarks[pip].y
        - landmarks[0].y

    )


    return (
        tip_distance
        >
        pip_distance * 1.05
    )


# ============================================================
# OPEN PALM
# ============================================================

def is_open_palm(landmarks):

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


    return (
        index
        and
        middle
        and
        ring
        and
        pinky
    )


# ============================================================
# CLASSIFY GESTURE
# ============================================================

def classify_gesture(landmarks):

    wrist = landmarks[0]


    # ========================================================
    # STOP
    #
    # OPEN PALM ONLY
    # ========================================================

    if is_open_palm(landmarks):

        return "STOP"


    # ========================================================
    # INDEX
    #
    # Keep existing working index behavior.
    # ========================================================

    if finger_extended(
        landmarks,
        8,
        6
    ):

        direction = get_direction(
            wrist,
            landmarks[8]
        )

        if direction != "UNKNOWN":

            return direction


    # ========================================================
    # THUMB
    #
    # Thumb controls all four directions.
    # ========================================================

    thumb_direction = get_thumb_direction(
        landmarks
    )


    if thumb_direction != "UNKNOWN":

        return thumb_direction


    return "UNKNOWN"


# ============================================================
# COMMAND
# ============================================================

def gesture_to_command(landmarks):

    gesture = classify_gesture(
        landmarks
    )


    if gesture == "FORWARD":

        return "MOVE_FORWARD"


    if gesture == "BACKWARD":

        return "MOVE_BACKWARD"


    if gesture == "LEFT":

        return "TURN_LEFT"


    if gesture == "RIGHT":

        return "TURN_RIGHT"


    if gesture == "STOP":

        return "STOP"


    return "IDLE"