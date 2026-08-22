class PIDController:

    def __init__(self, kp=1.0, ki=0.0, kd=0.05, output_min=-1.0, output_max=1.0):

        self.kp = kp
        self.ki = ki
        self.kd = kd

        self.output_min = output_min
        self.output_max = output_max

        self.integral = 0.0
        self.previous_error = 0.0

    def update(self, target, measured, dt):

        if dt <= 0:
            return 0.0

        error = target - measured

        self.integral += error * dt

        derivative = (
            error - self.previous_error
        ) / dt

        output = (
            self.kp * error
            + self.ki * self.integral
            + self.kd * derivative
        )

        output = max(
            self.output_min,
            min(self.output_max, output)
        )

        self.previous_error = error

        return output

    def reset(self):

        self.integral = 0.0
        self.previous_error = 0.0
