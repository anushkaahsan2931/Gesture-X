# ============================================================
# GESTURE-X
# DIFFERENTIAL DRIVE MOTOR CONTROLLER
# ============================================================

import math

from src.control.pid_controller import PIDController

class MotorController:

    def __init__(self):

        # ----------------------------------------------------
        # Maximum simulated wheel speed
        # ----------------------------------------------------

        self.max_wheel_speed = 1.0


        # ----------------------------------------------------
        # Left motor PID
        # ----------------------------------------------------

        self.left_pid = PIDController(

            kp=1.2,
            ki=0.15,
            kd=0.05,

            output_min=-1.0,
            output_max=1.0

        )


        # ----------------------------------------------------
        # Right motor PID
        # ----------------------------------------------------

        self.right_pid = PIDController(

            kp=1.2,
            ki=0.15,
            kd=0.05,

            output_min=-1.0,
            output_max=1.0

        )


        # ----------------------------------------------------
        # Target wheel velocities
        # ----------------------------------------------------

        self.target_left = 0.0
        self.target_right = 0.0


        # ----------------------------------------------------
        # Simulated encoder measurements
        # ----------------------------------------------------

        self.measured_left = 0.0
        self.measured_right = 0.0


        # ----------------------------------------------------
        # Motor outputs
        # ----------------------------------------------------

        self.left_motor_output = 0.0
        self.right_motor_output = 0.0


    # ========================================================
    # SET TARGET SPEEDS
    # ========================================================

    def set_target_velocity(
        self,
        left_velocity,
        right_velocity
    ):

        self.target_left = max(

            -self.max_wheel_speed,

            min(
                self.max_wheel_speed,
                left_velocity
            )

        )


        self.target_right = max(

            -self.max_wheel_speed,

            min(
                self.max_wheel_speed,
                right_velocity
            )

        )


    # ========================================================
    # SIMULATED ENCODER
    # ========================================================

    def update_encoder_feedback(self, dt):

        if dt <= 0:

            return


        # ----------------------------------------------------
        # First-order motor response
        #
        # The simulated wheel doesn't instantly reach the
        # commanded speed. This creates something for the
        # PID controller to correct.
        # ----------------------------------------------------

        response = 0.35


        self.measured_left += (

            self.target_left
            - self.measured_left

        ) * response


        self.measured_right += (

            self.target_right
            - self.measured_right

        ) * response


    # ========================================================
    # PID UPDATE
    # ========================================================

    def update(self, dt):

        if dt <= 0:

            return


        # ----------------------------------------------------
        # Simulated encoder feedback
        # ----------------------------------------------------

        self.update_encoder_feedback(dt)


        # ----------------------------------------------------
        # LEFT MOTOR PID
        # ----------------------------------------------------

        self.left_motor_output = (

            self.left_pid.update(

                self.target_left,

                self.measured_left,

                dt

            )

        )


        # ----------------------------------------------------
        # RIGHT MOTOR PID
        # ----------------------------------------------------

        self.right_motor_output = (

            self.right_pid.update(

                self.target_right,

                self.measured_right,

                dt

            )

        )


    # ========================================================
    # STOP
    # ========================================================

    def stop(self):

        self.target_left = 0.0
        self.target_right = 0.0

        self.left_motor_output = 0.0
        self.right_motor_output = 0.0

        self.measured_left = 0.0
        self.measured_right = 0.0


        self.left_pid.reset()
        self.right_pid.reset()


    # ========================================================
    # TELEMETRY
    # ========================================================

    def get_status(self):

        return {

            "target_left":
                self.target_left,

            "target_right":
                self.target_right,

            "measured_left":
                self.measured_left,

            "measured_right":
                self.measured_right,

            "left_output":
                self.left_motor_output,

            "right_output":
                self.right_motor_output

        }

