from src.vision.gesture_controller import gesture_to_command


class GestureRobotController:

    def __init__(self, robot):

        self.robot = robot

        self.last_command = "IDLE"


    # ========================================================
    # PROCESS GESTURE
    # ========================================================

    def process_gesture(self, landmarks):

        command = gesture_to_command(
            landmarks
        )

        self.last_command = command


        # ====================================================
        # FORWARD
        # ====================================================

        if command == "MOVE_FORWARD":

            self.robot.move_forward(
                0.10
            )


        # ====================================================
        # BACKWARD
        # ====================================================

        elif command == "MOVE_BACKWARD":

            self.robot.move_forward(
                -0.10
            )


        # ====================================================
        # LEFT
        # ====================================================

        elif command == "TURN_LEFT":

            self.robot.turn_left(
                5
            )


        # ====================================================
        # RIGHT
        # ====================================================

        elif command == "TURN_RIGHT":

            self.robot.turn_right(
                5
            )


        # ====================================================
        # STOP
        # ====================================================

        elif command == "STOP":

            pass


        # ====================================================
        # IDLE
        # ====================================================

        elif command == "IDLE":

            pass


        return command