# ============================================================
# ROBOT COMMAND INTERFACE
# ============================================================


class RobotCommandInterface:

    def __init__(self, robot):

        self.robot = robot


    # ========================================================
    # FORWARD
    # ========================================================

    def move_forward(self):

        self.robot.move_forward(0.12)


    # ========================================================
    # BACKWARD
    # ========================================================

    def move_backward(self):

        self.robot.move_forward(-0.12)


    # ========================================================
    # LEFT
    # ========================================================

    def turn_left(self):

        self.robot.turn_left(10)


    # ========================================================
    # RIGHT
    # ========================================================

    def turn_right(self):

        self.robot.turn_right(10)


    # ========================================================
    # STOP
    # ========================================================

    def stop(self):

        # The simulator does not have continuous motor motion.
        # Therefore STOP simply means "do not issue movement."

        pass


    # ========================================================
    # COMMAND ROUTER
    # ========================================================

    def execute(self, command):

        if command == "MOVE_FORWARD":

            self.move_forward()


        elif command == "MOVE_BACKWARD":

            self.move_backward()


        elif command == "TURN_LEFT":

            self.turn_left()


        elif command == "TURN_RIGHT":

            self.turn_right()


        elif command == "STOP":

            self.stop()