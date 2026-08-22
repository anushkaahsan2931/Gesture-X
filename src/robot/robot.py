import math

import cv2
import mediapipe as mp
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import Button

from src.navigation.planner import AStarPlanner
from src.vision.gesture_controller import gesture_to_command
from src.control.motor_controller import MotorController


# ============================================================
# ROBOT — DIFFERENTIAL DRIVE MODEL
# ============================================================

class Robot:

    def __init__(self, x=2.0, y=2.0):

        self.start_x = x
        self.start_y = y

        self.x = x
        self.y = y

        self.heading = 0.0

        # Differential-drive parameters
        self.wheel_base = 0.30
        self.wheel_radius = 0.05

        # Wheel velocities
        self.left_wheel_velocity = 0.0
        self.right_wheel_velocity = 0.0

        # Robot velocity
        self.linear_velocity = 0.0
        self.angular_velocity = 0.0

    # ========================================================
    # DIFFERENTIAL DRIVE
    # ========================================================

    def set_wheel_velocity(
        self,
        left_velocity,
        right_velocity
    ):

        self.left_wheel_velocity = left_velocity
        self.right_wheel_velocity = right_velocity

        self.linear_velocity = (
            self.right_wheel_velocity
            + self.left_wheel_velocity
        ) / 2.0

        self.angular_velocity = (
            self.right_wheel_velocity
            - self.left_wheel_velocity
        ) / self.wheel_base

    # ========================================================
    # CHECK WHETHER ROBOT CAN OCCUPY POSITION
    # ========================================================

    def can_move_to(self, new_x, new_y):

        # Robot body radius.
        # This means the entire robot must remain inside
        # the floor and outside obstacles.
        robot_radius = 0.30

        # ====================================================
        # FLOOR BOUNDARIES
        # ====================================================

        if new_x - robot_radius < 0.3:
            return False

        if new_x + robot_radius > 9.7:
            return False

        if new_y - robot_radius < 0.3:
            return False

        if new_y + robot_radius > 7.7:
            return False

        # ====================================================
        # STATIC OBSTACLES
        # ====================================================

        for ox, oy, width, height in static_obstacles:

            closest_x = max(
                ox,
                min(new_x, ox + width)
            )

            closest_y = max(
                oy,
                min(new_y, oy + height)
            )

            distance = math.hypot(
                new_x - closest_x,
                new_y - closest_y
            )

            if distance < robot_radius:
                return False

        # ====================================================
        # DYNAMIC OBSTACLE
        # ====================================================

        if dynamic_obstacle["active"]:

            ox = dynamic_obstacle["x"]
            oy = dynamic_obstacle["y"]
            width = dynamic_obstacle["width"]
            height = dynamic_obstacle["height"]

            closest_x = max(
                ox,
                min(new_x, ox + width)
            )

            closest_y = max(
                oy,
                min(new_y, oy + height)
            )

            distance = math.hypot(
                new_x - closest_x,
                new_y - closest_y
            )

            if distance < robot_radius:
                return False

        return True

    # ========================================================
    # DIFFERENTIAL DRIVE MOVEMENT
    # ========================================================

    def set_wheel_velocity(
        self,
        left_velocity,
        right_velocity
    ):

        self.left_wheel_velocity = left_velocity
        self.right_wheel_velocity = right_velocity

        self.linear_velocity = (
            self.right_wheel_velocity
            + self.left_wheel_velocity
        ) / 2.0

        self.angular_velocity = (
            self.right_wheel_velocity
            - self.left_wheel_velocity
        ) / self.wheel_base

    # ========================================================
    # MOVE FORWARD / BACKWARD
    # ========================================================

    def move_forward(self, distance=0.1):

        velocity = distance

        self.set_wheel_velocity(
            velocity,
            velocity
        )

        angle = math.radians(self.heading)

        new_x = (
            self.x
            + distance * math.cos(angle)
        )

        new_y = (
            self.y
            + distance * math.sin(angle)
        )

        # ====================================================
        # FULL COLLISION / BOUNDARY PROTECTION
        # ====================================================

        # This applies to BOTH forward and backward movement.
        # Therefore the robot cannot drive into an obstacle
        # or boundary from behind either.
        if self.can_move_to(new_x, new_y):

            self.x = new_x
            self.y = new_y

        else:

            self.stop_motors()

            return False

        self.stop_motors()

        return True

    # ========================================================
    # TURN LEFT
    # ========================================================

    def turn_left(self, degrees=5):

        self.set_wheel_velocity(
            -0.15,
            0.15
        )

        self.heading += degrees

        if self.heading >= 360:
            self.heading -= 360

        self.stop_motors()

    # ========================================================
    # TURN RIGHT
    # ========================================================

    def turn_right(self, degrees=5):

        self.set_wheel_velocity(
            0.15,
            -0.15
        )

        self.heading -= degrees

        if self.heading < 0:
            self.heading += 360

        self.stop_motors()

    # ========================================================
    # STOP MOTORS
    # ========================================================

    def stop_motors(self):

        self.left_wheel_velocity = 0.0
        self.right_wheel_velocity = 0.0

        self.linear_velocity = 0.0
        self.angular_velocity = 0.0

    # ========================================================
    # RESET
    # ========================================================

    def reset(self):

        self.x = self.start_x
        self.y = self.start_y

        self.heading = 0.0

        self.stop_motors()


# ============================================================
# MOTOR CONTROLLER
# ============================================================

try:

    motor_controller = MotorController()

except Exception:

    motor_controller = None


# ============================================================
# ENVIRONMENT
# ============================================================

robot = Robot()


static_obstacles = [

    (4, 1, 1, 3),

    (7, 4, 1, 3)

]


dynamic_obstacle = {

    "x": 5.0,

    "y": 5.0,

    "width": 0.8,

    "height": 0.8,

    "active": False

}


target_x = 6.0
target_y = 6.5


# ============================================================
# SPEED CONTROL
# ============================================================

SPEED_LEVELS = {

    "1": 0.25,

    "2": 0.50,

    "3": 0.75,

    "4": 1.00,

    "5": 1.25

}


speed_level = "4"

speed_multiplier = SPEED_LEVELS[speed_level]


# ============================================================
# BATTERY / POWER MANAGEMENT
# ============================================================

battery_level = 100.0

BATTERY_LOW_THRESHOLD = 20.0
BATTERY_CRITICAL_THRESHOLD = 5.0

BASE_MOVEMENT_DRAIN = 0.08
TURNING_DRAIN = 0.05


def update_battery():

    global battery_level

    # Battery is updated based on actual commanded motion.
    if abs(robot.linear_velocity) > 0:

        battery_level -= (
            BASE_MOVEMENT_DRAIN
            * speed_multiplier
        )

    if abs(robot.angular_velocity) > 0:

        battery_level -= (
            TURNING_DRAIN
            * speed_multiplier
        )

    battery_level = max(
        0.0,
        min(100.0, battery_level)
    )


def consume_battery_for_movement():

    global battery_level

    battery_level -= (
        BASE_MOVEMENT_DRAIN
        * speed_multiplier
    )

    battery_level = max(
        0.0,
        min(100.0, battery_level)
    )


def consume_battery_for_turn():

    global battery_level

    battery_level -= (
        TURNING_DRAIN
        * speed_multiplier
    )

    battery_level = max(
        0.0,
        min(100.0, battery_level)
    )


def battery_status():

    if battery_level <= BATTERY_CRITICAL_THRESHOLD:

        return "CRITICAL"

    elif battery_level <= BATTERY_LOW_THRESHOLD:

        return "LOW"

    return "NORMAL"


# ============================================================
# BATTERY WARNING
# ============================================================

battery_warning_visible = True
battery_warning_counter = 0


# ============================================================
# SPEED SETTER
# ============================================================

def set_speed(level):

    global speed_level
    global speed_multiplier

    if level in SPEED_LEVELS:

        speed_level = level

        speed_multiplier = SPEED_LEVELS[level]

        print(
            f"SPEED LEVEL {speed_level} "
            f"({speed_multiplier * 100:.0f}%)"
        )


# ============================================================
# PLANNER
# ============================================================

planner = AStarPlanner()


def calculate_path():

    obstacles = list(static_obstacles)

    if dynamic_obstacle["active"]:

        obstacles.append(

            (
                dynamic_obstacle["x"],
                dynamic_obstacle["y"],
                dynamic_obstacle["width"],
                dynamic_obstacle["height"]
            )

        )

    return planner.plan(

        (robot.x, robot.y),

        (target_x, target_y),

        obstacles

    )


path = calculate_path()

path_index = 0


# ============================================================
# MODES
# ============================================================

MODE_AUTONOMOUS = "AUTONOMOUS"

MODE_MANUAL = "MANUAL"

MODE_GESTURE = "GESTURE"

MODE_STOPPED = "EMERGENCY STOP"


current_mode = MODE_AUTONOMOUS


# ============================================================
# STATES
# ============================================================

STATE_NAVIGATE = "AUTONOMOUS NAVIGATION"

STATE_AVOID = "OBSTACLE DETECTED"

STATE_REPLAN = "REPLANNING ROUTE"

STATE_REACHED = "TARGET REACHED"


robot_state = STATE_NAVIGATE

avoidance_steps = 0


# ============================================================
# GESTURE STATUS
# ============================================================

last_gesture = "IDLE"

last_command = "IDLE"


# ============================================================
# LIDAR
# ============================================================

sensor_range = 2.0


sensor_angles = [

    -90,
    -60,
    -30,
    0,
    30,
    60,
    90

]


sensor_names = [

    "Right",
    "Front-Right",
    "Front",
    "Front-Left",
    "Left",
    "Back-Left",
    "Back"

]


sensor_rays = []


# ============================================================
# FIGURE
# ============================================================

fig = plt.figure(
    figsize=(14, 8)
)


ax = fig.add_axes(
    [0.05, 0.08, 0.60, 0.84]
)


# ============================================================
# ROBOTICS TEST FLOOR
# ============================================================

ax.set_xticks(range(0, 11, 1))
ax.set_yticks(range(0, 9, 1))

ax.grid(
    True,
    linestyle=":",
    linewidth=0.6,
    alpha=0.35
)

ax.set_axisbelow(True)


# ============================================================
# PROFESSIONAL WAREHOUSE SHELVES
# ============================================================

shelf_graphics = []

for x, y, width, height in static_obstacles:

    shelf = patches.Rectangle(
        (x, y),
        width,
        height,
        linewidth=2
    )

    ax.add_patch(shelf)

    shelf_graphics.append(shelf)

    shelf_levels = 3

    for level in range(1, shelf_levels):

        shelf_y = y + (
            height * level / shelf_levels
        )

        ax.plot(
            [x, x + width],
            [shelf_y, shelf_y],
            linewidth=1.5
        )

    ax.plot(
        [x + width * 0.18, x + width * 0.18],
        [y, y + height],
        linewidth=1.2
    )

    ax.plot(
        [x + width * 0.82, x + width * 0.82],
        [y, y + height],
        linewidth=1.2
    )


# ============================================================
# DYNAMIC OBSTACLE
# ============================================================

dynamic_patch = patches.Rectangle(

    (
        dynamic_obstacle["x"],
        dynamic_obstacle["y"]
    ),

    dynamic_obstacle["width"],
    dynamic_obstacle["height"],

    visible=False

)

ax.add_patch(
    dynamic_patch
)


# ============================================================
# TARGET / DOCKING STATION
# ============================================================

target_outer = patches.Circle(
    (
        target_x,
        target_y
    ),
    0.38,
    fill=False,
    linewidth=2
)

target_inner = patches.Circle(
    (
        target_x,
        target_y
    ),
    0.20,
    fill=False,
    linewidth=2
)

ax.add_patch(target_outer)
ax.add_patch(target_inner)


ax.plot(
    [
        target_x - 0.28,
        target_x + 0.28
    ],
    [
        target_y,
        target_y
    ],
    linewidth=1
)


ax.plot(
    [
        target_x,
        target_x
    ],
    [
        target_y - 0.28,
        target_y + 0.28
    ],
    linewidth=1
)


target_label = ax.text(
    target_x,
    target_y - 0.55,
    "DOCK",
    fontsize=8,
    ha="center"
)


# ============================================================
# A* PATH
# ============================================================

path_line, = ax.plot(

    [],
    [],

    linestyle="--",

    linewidth=1.5,

    label="A* Route"

)


def draw_path():

    if not path:

        path_line.set_data(
            [],
            []
        )

        return

    path_x = [

        point[0]

        for point in path

    ]

    path_y = [

        point[1]

        for point in path

    ]

    path_line.set_data(

        path_x,
        path_y

    )


draw_path()


# ============================================================
# BATTERY DISPLAY — TOP LEFT
# ============================================================

battery_display = ax.text(
    1.10,
    7.65,
    "BATTERY: 100.0% | POWER: NORMAL",
    fontsize=9,
    fontweight="bold",
    verticalalignment="top"
)


battery_warning = ax.text(
    5.8,
    7.65,
    "",
    fontsize=9,
    fontweight="bold",
    verticalalignment="top",
    color="red"
)


# ============================================================
# ROBOT GRAPHICS
# ============================================================

robot_shape = patches.Circle(

    (
        robot.x,
        robot.y
    ),

    0.3,

    visible=False

)

ax.add_patch(
    robot_shape
)


# Robot chassis
robot_body = patches.FancyBboxPatch(
    (
        robot.x - 0.34,
        robot.y - 0.23
    ),
    0.68,
    0.46,
    boxstyle="round,pad=0.03,rounding_size=0.08",
    linewidth=2
)

ax.add_patch(robot_body)


# Left drive wheel
left_wheel = patches.FancyBboxPatch(
    (
        robot.x - 0.32,
        robot.y - 0.30
    ),
    0.18,
    0.10,
    boxstyle="round,pad=0.02",
    linewidth=1
)

ax.add_patch(left_wheel)


# Right drive wheel
right_wheel = patches.FancyBboxPatch(
    (
        robot.x - 0.32,
        robot.y + 0.20
    ),
    0.18,
    0.10,
    boxstyle="round,pad=0.02",
    linewidth=1
)

ax.add_patch(right_wheel)


# LiDAR sensor
lidar_sensor = patches.Circle(
    (
        robot.x,
        robot.y
    ),
    0.09,
    linewidth=2
)

ax.add_patch(lidar_sensor)


# Front sensor
front_sensor = patches.Circle(
    (
        robot.x + 0.28,
        robot.y
    ),
    0.045,
    linewidth=1.5
)

ax.add_patch(front_sensor)


heading_line, = ax.plot(

    [],
    [],

    linewidth=3

)


# ============================================================
# LIDAR SENSOR RAYS
# ============================================================

for _ in sensor_angles:

    ray, = ax.plot(

        [],
        [],

        linestyle=":",

        linewidth=1

    )

    sensor_rays.append(ray)


# ============================================================
# RIGHT-SIDE TELEMETRY
# ============================================================

telemetry = fig.text(

    0.70,

    0.96,

    "",

    fontsize=10,

    verticalalignment="top",

    family="monospace"

)


# ============================================================
# RIGHT-SIDE SYSTEM STATUS
# ============================================================

status_text = fig.text(

    0.70,

    0.42,

    "",

    fontsize=10,

    verticalalignment="top",

    fontweight="bold"

)


# ============================================================
# GESTURE CONTROL BUTTON
# ============================================================

button_ax = fig.add_axes(

    [0.70, 0.015, 0.13, 0.045]

)


gesture_button = Button(

    button_ax,

    "GESTURE MODE"

)


# ============================================================
# GESTURE COMMAND DISPLAY
# ============================================================

gesture_status_text = fig.text(

    0.845,

    0.037,

    "GESTURE: IDLE",

    fontsize=10,

    verticalalignment="center",

    fontweight="bold"

)


# ============================================================
# CONTROL HELP
# ============================================================

controls_text = fig.text(

    0.05,

    0.025,

    "SPACE = Emergency Stop    |    M = Manual    |    A = Autonomous    |    G = Gesture    |    R = Reset",

    fontsize=9

)


# ============================================================
# LIDAR SENSOR CALCULATION
# ============================================================

def calculate_sensor_distance(angle_degrees):

    angle = math.radians(

        robot.heading
        + angle_degrees

    )

    step = 0.05

    distance = 0


    while distance <= sensor_range:

        test_x = (

            robot.x
            + distance
            * math.cos(angle)

        )

        test_y = (

            robot.y
            + distance
            * math.sin(angle)

        )


        # Boundary detection

        if (

            test_x < 0.3
            or
            test_x > 9.7
            or
            test_y < 0.3
            or
            test_y > 7.7

        ):

            return distance


        # Static obstacles

        for ox, oy, width, height in static_obstacles:

            if (

                ox <= test_x <= ox + width

                and

                oy <= test_y <= oy + height

            ):

                return distance


        # Dynamic obstacle

        if dynamic_obstacle["active"]:

            ox = dynamic_obstacle["x"]
            oy = dynamic_obstacle["y"]

            width = dynamic_obstacle["width"]
            height = dynamic_obstacle["height"]


            if (

                ox <= test_x <= ox + width

                and

                oy <= test_y <= oy + height

            ):

                return distance


        distance += step


    return sensor_range


# ============================================================
# READ LIDAR
# ============================================================

def get_sensor_readings():

    readings = {}


    for angle, name in zip(

        sensor_angles,
        sensor_names

    ):

        readings[name] = (

            calculate_sensor_distance(angle)

        )


    return readings


# ============================================================
# OBSTACLE DETECTION
# ============================================================

def obstacle_detected(readings):

    return (

        readings["Front"] < 0.8

        or

        readings["Front-Left"] < 0.5

        or

        readings["Front-Right"] < 0.5

    )


# ============================================================
# UPDATE GESTURE DISPLAY
# ============================================================

def update_gesture_display(command):

    if command == "MOVE_FORWARD":

        gesture_status_text.set_text(
            "GESTURE: FORWARD"
        )

    elif command == "MOVE_BACKWARD":

        gesture_status_text.set_text(
            "GESTURE: BACKWARD"
        )

    elif command == "TURN_LEFT":

        gesture_status_text.set_text(
            "GESTURE: LEFT"
        )

    elif command == "TURN_RIGHT":

        gesture_status_text.set_text(
            "GESTURE: RIGHT"
        )

    elif command == "STOP":

        gesture_status_text.set_text(
            "GESTURE: STOP"
        )

    else:

        gesture_status_text.set_text(
            "GESTURE: IDLE"
        )


# ============================================================
# UPDATE ROBOT DISPLAY
# ============================================================

def update_robot():

    global robot_state

    # ========================================================
    # BASIC ROBOT POSITION
    # ========================================================

    robot_shape.center = (
        robot.x,
        robot.y
    )

    angle = math.radians(
        robot.heading
    )


    # ========================================================
    # UPDATE ROBOT GRAPHICS
    # ========================================================

    robot_body.set_x(
        robot.x - 0.34
    )

    robot_body.set_y(
        robot.y - 0.23
    )


    left_wheel.set_x(
        robot.x - 0.34
    )

    left_wheel.set_y(
        robot.y - 0.28
    )


    right_wheel.set_x(
        robot.x - 0.34
    )

    right_wheel.set_y(
        robot.y + 0.18
    )


    lidar_sensor.center = (
        robot.x,
        robot.y
    )


    front_sensor.center = (
        robot.x
        + 0.28
        * math.cos(angle),

        robot.y
        + 0.28
        * math.sin(angle)
    )


    # ========================================================
    # HEADING INDICATOR
    # ========================================================

    heading_line.set_data(

        [
            robot.x,

            robot.x
            + 0.5
            * math.cos(angle)
        ],

        [
            robot.y,

            robot.y
            + 0.5
            * math.sin(angle)
        ]

    )


    # ========================================================
    # LIDAR SENSOR RAYS
    # ========================================================

    readings = get_sensor_readings()


    for ray, sensor_angle, sensor_name in zip(

        sensor_rays,
        sensor_angles,
        sensor_names

    ):

        distance = readings[
            sensor_name
        ]


        ray_angle = math.radians(

            robot.heading
            + sensor_angle

        )


        end_x = (

            robot.x
            + distance
            * math.cos(ray_angle)

        )


        end_y = (

            robot.y
            + distance
            * math.sin(ray_angle)

        )


        ray.set_data(

            [
                robot.x,
                end_x
            ],

            [
                robot.y,
                end_y
            ]

        )


    # ========================================================
    # BATTERY DISPLAY
    # ========================================================

    status = battery_status()


    battery_display.set_text(

        f"BATTERY: {battery_level:.1f}%"
        f"  |  POWER: {status}"

    )


    # ========================================================
    # BATTERY WARNING
    # ========================================================

    if status == "CRITICAL":

        battery_warning.set_text(
            "⚠ CRITICAL — ROBOT STOPPED"
        )

        battery_warning.set_visible(
            battery_warning_visible
        )

    elif status == "LOW":

        battery_warning.set_text(
            "⚠ LOW BATTERY"
        )

        battery_warning.set_visible(True)

    else:

        battery_warning.set_text("")

        battery_warning.set_visible(False)


    # ========================================================
    # TELEMETRY
    # ========================================================

    telemetry_text = (

        "GESTURE-X TELEMETRY\n"

        "────────────────────────\n\n"

        f"Position X : {robot.x:5.2f} m\n"

        f"Position Y : {robot.y:5.2f} m\n"

        f"Heading    : {robot.heading:5.1f}°\n\n"

        f"Target X   : {target_x:5.2f} m\n"

        f"Target Y   : {target_y:5.2f} m\n\n"

        f"A* Nodes   : {len(path):5d}\n"

        f"Waypoint   : {path_index:5d}\n\n"

        f"Speed      : {speed_level} "
        f"({speed_multiplier * 100:.0f}%)\n\n"

        "LiDAR\n"

        "────────────────────────\n"

        f"Front      : {readings['Front']:5.2f} m\n"

        f"Front-L    : {readings['Front-Left']:5.2f} m\n"

        f"Front-R    : {readings['Front-Right']:5.2f} m\n"

        f"Left       : {readings['Left']:5.2f} m\n"

        f"Right      : {readings['Right']:5.2f} m\n"

        f"Back       : {readings['Back']:5.2f} m\n\n"

        f"Gesture    : {last_gesture}\n"

        f"Command    : {last_command}\n"

    )


    telemetry.set_text(
        telemetry_text
    )


    # ========================================================
    # SYSTEM STATUS
    # ========================================================

    status_text.set_text(

        "SYSTEM STATUS\n"

        "────────────────────────\n\n"

        f"MODE: {current_mode}\n\n"

        f"{robot_state}\n\n"

        "Navigation Stack\n\n"

        "✓ LiDAR perception\n"

        "✓ A* path planning\n"

        "✓ Dynamic obstacle detection\n"

        "✓ Route replanning\n"

        "✓ Manual control\n"

        "✓ Gesture control"

    )


    fig.canvas.draw_idle()


# ============================================================
# AUTONOMOUS NAVIGATION
# ============================================================

def autonomous_navigation():

    global path
    global path_index
    global robot_state
    global avoidance_steps


    # ========================================================
    # DYNAMIC OBSTACLE
    # ========================================================

    if robot.x > 3.2:

        dynamic_obstacle["active"] = True

        dynamic_patch.set_visible(True)

    else:

        dynamic_obstacle["active"] = False

        dynamic_patch.set_visible(False)


    # ========================================================
    # DISTANCE TO TARGET
    # ========================================================

    distance_to_target = math.hypot(

        target_x - robot.x,
        target_y - robot.y

    )


    # ========================================================
    # TARGET CHECK
    # ========================================================

    if distance_to_target < 0.12:

        robot.stop_motors()

        robot_state = STATE_REACHED

        return


    # ========================================================
    # RECOVER FROM TARGET REACHED
    # ========================================================

    if robot_state == STATE_REACHED:

        path = calculate_path()

        path_index = 0

        avoidance_steps = 0

        draw_path()


        if path:

            robot_state = STATE_NAVIGATE

        else:

            robot_state = "NO PATH FOUND"

            return


    # ========================================================
    # RECOVER IF PATH EMPTY
    # ========================================================

    if not path:

        path = calculate_path()

        path_index = 0

        draw_path()


        if not path:

            robot_state = "NO PATH FOUND"

            return


        robot_state = STATE_NAVIGATE


    # ========================================================
    # NORMAL NAVIGATION
    # ========================================================

    if robot_state == STATE_NAVIGATE:

        readings = get_sensor_readings()


        if obstacle_detected(readings):

            robot.stop_motors()

            robot_state = STATE_AVOID

            avoidance_steps = 0

            return


        if path_index >= len(path):

            distance_to_target = math.hypot(

                target_x - robot.x,
                target_y - robot.y

            )


            if distance_to_target < 0.20:

                robot_state = STATE_REACHED

                return


            path = calculate_path()

            path_index = 0

            draw_path()


            if not path:

                robot_state = "NO PATH FOUND"

                return


        waypoint_x, waypoint_y = path[path_index]


        dx = waypoint_x - robot.x

        dy = waypoint_y - robot.y


        distance = math.hypot(
            dx,
            dy
        )


        if distance < 0.12:

            path_index += 1

            return


        target_angle = math.degrees(

            math.atan2(
                dy,
                dx
            )

        )


        angle_difference = (

            target_angle
            - robot.heading

        )


        while angle_difference > 180:

            angle_difference -= 360


        while angle_difference < -180:

            angle_difference += 360


        if abs(angle_difference) > 5:

            if angle_difference > 0:

                robot.turn_left(
                    5 * speed_multiplier
                )

                consume_battery_for_turn()

            else:

                robot.turn_right(
                    5 * speed_multiplier
                )

                consume_battery_for_turn()

        else:

            moved = robot.move_forward(
                0.1 * speed_multiplier
            )

            if moved:

                consume_battery_for_movement()

            else:

                robot.stop_motors()

                robot_state = "AUTONOMOUS: PATH BLOCKED"


    # ========================================================
    # AVOIDANCE
    # ========================================================

    elif robot_state == STATE_AVOID:

        avoidance_steps += 1

        robot.stop_motors()

        robot.turn_left(
            15 * speed_multiplier
        )

        consume_battery_for_turn()

        moved = robot.move_forward(
            0.08 * speed_multiplier
        )

        if moved:

            consume_battery_for_movement()

        else:

            robot.stop_motors()


        if avoidance_steps >= 8:

            robot_state = STATE_REPLAN


    # ========================================================
    # REPLANNING
    # ========================================================

    elif robot_state == STATE_REPLAN:

        path = calculate_path()

        path_index = 0

        avoidance_steps = 0

        draw_path()


        if path:

            robot_state = STATE_NAVIGATE

        else:

            robot_state = "NO PATH FOUND"


    # ========================================================
    # RECOVERY FROM NO PATH
    # ========================================================

    elif robot_state == "NO PATH FOUND":

        path = calculate_path()

        path_index = 0

        draw_path()


        if path:

            robot_state = STATE_NAVIGATE


# ============================================================
# MANUAL CONTROL
# ============================================================

def manual_control(key):

    global robot_state


    if current_mode != MODE_MANUAL:

        return


    readings = get_sensor_readings()


    # ========================================================
    # FORWARD — OBSTACLE PROTECTION
    # ========================================================

    if key == "up":

        if readings["Front"] < 0.65:

            robot.stop_motors()

            robot_state = "MANUAL: FORWARD BLOCKED"

            return


        moved = robot.move_forward(
            0.15 * speed_multiplier
        )

        if moved:

            consume_battery_for_movement()

            robot_state = "MANUAL CONTROL"

        else:

            robot.stop_motors()

            robot_state = "MANUAL: FORWARD BLOCKED"


    # ========================================================
    # BACKWARD — OBSTACLE PROTECTION
    # ========================================================

    elif key == "down":

        if readings["Back"] < 0.65:

            robot.stop_motors()

            robot_state = "MANUAL: BACKWARD BLOCKED"

            return


        moved = robot.move_forward(
            -0.15 * speed_multiplier
        )

        if moved:

            consume_battery_for_movement()

            robot_state = "MANUAL CONTROL"

        else:

            robot.stop_motors()

            robot_state = "MANUAL: BACKWARD BLOCKED"


    # ========================================================
    # LEFT — OBSTACLE PROTECTION
    # ========================================================

    elif key == "left":

        if readings["Front-Left"] < 0.45:

            robot.stop_motors()

            robot_state = "MANUAL: LEFT BLOCKED"

            return


        robot.turn_left(
            10 * speed_multiplier
        )

        consume_battery_for_turn()

        robot_state = "MANUAL CONTROL"


    # ========================================================
    # RIGHT — OBSTACLE PROTECTION
    # ========================================================

    elif key == "right":

        if readings["Front-Right"] < 0.45:

            robot.stop_motors()

            robot_state = "MANUAL: RIGHT BLOCKED"

            return


        robot.turn_right(
            10 * speed_multiplier
        )

        consume_battery_for_turn()

        robot_state = "MANUAL CONTROL"


# ============================================================
# GESTURE CONTROL
# ============================================================

def execute_gesture(command):

    global robot_state


    if current_mode != MODE_GESTURE:

        return


    readings = get_sensor_readings()


    # ========================================================
    # FORWARD
    # ========================================================

    if command == "MOVE_FORWARD":

        if readings["Front"] < 0.65:

            robot.stop_motors()

            robot_state = "GESTURE: FORWARD BLOCKED"

            return


        moved = robot.move_forward(
            0.12 * speed_multiplier
        )

        if moved:

            consume_battery_for_movement()

            robot_state = "GESTURE: FORWARD"

        else:

            robot.stop_motors()

            robot_state = "GESTURE: FORWARD BLOCKED"


    # ========================================================
    # BACKWARD
    # ========================================================

    elif command == "MOVE_BACKWARD":

        if readings["Back"] < 0.65:

            robot.stop_motors()

            robot_state = "GESTURE: BACKWARD BLOCKED"

            return


        moved = robot.move_forward(
            -0.12 * speed_multiplier
        )

        if moved:

            consume_battery_for_movement()

            robot_state = "GESTURE: BACKWARD"

        else:

            robot.stop_motors()

            robot_state = "GESTURE: BACKWARD BLOCKED"


    # ========================================================
    # LEFT
    # ========================================================

    elif command == "TURN_LEFT":

        if readings["Front-Left"] < 0.45:

            robot.stop_motors()

            robot_state = "GESTURE: LEFT BLOCKED"

            return


        robot.turn_left(
            10 * speed_multiplier
        )

        consume_battery_for_turn()

        robot_state = "GESTURE: LEFT"


    # ========================================================
    # RIGHT
    # ========================================================

    elif command == "TURN_RIGHT":

        if readings["Front-Right"] < 0.45:

            robot.stop_motors()

            robot_state = "GESTURE: RIGHT BLOCKED"

            return


        robot.turn_right(
            10 * speed_multiplier
        )

        consume_battery_for_turn()

        robot_state = "GESTURE: RIGHT"


    # ========================================================
    # STOP
    # ========================================================

    elif command == "STOP":

        robot.stop_motors()

        robot_state = "GESTURE: STOP"


# ============================================================
# GESTURE CAMERA
# ============================================================

camera = None

hands = None


def start_gesture_camera():

    global camera
    global hands


    if camera is not None:

        return


    camera = cv2.VideoCapture(0)


    if not camera.isOpened():

        print(
            "ERROR: Could not open camera."
        )

        camera = None

        return


    hands = mp.solutions.hands.Hands(

        static_image_mode=False,

        max_num_hands=1,

        min_detection_confidence=0.6,

        min_tracking_confidence=0.6

    )


    print(
        "GESTURE MODE ENABLED"
    )


# ============================================================
# STOP GESTURE CAMERA
# ============================================================

def stop_gesture_camera():

    global camera
    global hands


    if camera is not None:

        camera.release()

        camera = None


    if hands is not None:

        hands.close()

        hands = None


    try:

        cv2.destroyWindow(
            "Gesture-X | Gesture Control"
        )

    except cv2.error:

        pass


# ============================================================
# PROCESS GESTURE
# ============================================================

def process_gesture():

    global last_gesture
    global last_command


    if camera is None or hands is None:

        return


    success, frame = camera.read()


    if not success:

        return


    frame = cv2.flip(
        frame,
        1
    )


    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )


    results = hands.process(rgb)


    command = "IDLE"

    last_gesture = "IDLE"


    # ========================================================
    # HAND DETECTED
    # ========================================================

    if results.multi_hand_landmarks:

        hand = results.multi_hand_landmarks[0]


        mp.solutions.drawing_utils.draw_landmarks(

            frame,

            hand,

            mp.solutions.hands.HAND_CONNECTIONS

        )


        command = gesture_to_command(
            hand.landmark
        )


        if command == "MOVE_FORWARD":

            last_gesture = "FORWARD"

        elif command == "MOVE_BACKWARD":

            last_gesture = "BACKWARD"

        elif command == "TURN_LEFT":

            last_gesture = "LEFT"

        elif command == "TURN_RIGHT":

            last_gesture = "RIGHT"

        elif command == "STOP":

            last_gesture = "STOP"

        else:

            last_gesture = "IDLE"


    else:

        last_gesture = "IDLE"

        command = "IDLE"


    last_command = command


    update_gesture_display(
        command
    )


    if command != "IDLE":

        execute_gesture(command)


    # ========================================================
    # CAMERA DISPLAY
    # ========================================================

    cv2.putText(

        frame,

        f"GESTURE: {last_gesture}",

        (20, 40),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.9,

        (0, 255, 255),

        2

    )


    cv2.putText(

        frame,

        f"COMMAND: {last_command}",

        (20, 80),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.75,

        (255, 255, 255),

        2

    )


    cv2.putText(

        frame,

        "Q = close camera",

        (20, 120),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.6,

        (255, 255, 255),

        2

    )


    cv2.imshow(

        "Gesture-X | Gesture Control",

        frame

    )


    if cv2.waitKey(1) & 0xFF == ord("q"):

        stop_gesture_camera()


# ============================================================
# GESTURE BUTTON
# ============================================================

def activate_gesture_button(event):

    global current_mode
    global robot_state


    if current_mode == MODE_GESTURE:

        return


    current_mode = MODE_GESTURE

    robot_state = "GESTURE CONTROL"


    start_gesture_camera()


    update_gesture_display(
        "IDLE"
    )


    update_robot()


    print(
        "GESTURE MODE"
    )


gesture_button.on_clicked(
    activate_gesture_button
)


# ============================================================
# KEYBOARD CONTROL
# ============================================================

def on_key(event):

    global current_mode
    global robot_state
    global path
    global path_index
    global avoidance_steps
    global battery_level


    key = event.key


    # ========================================================
    # SPEED CONTROL
    # ========================================================

    if key in SPEED_LEVELS:

        set_speed(key)

        update_robot()

        return


    # ========================================================
    # GESTURE MODE
    # ========================================================

    if key == "g":

        if current_mode != MODE_GESTURE:

            current_mode = MODE_GESTURE

            robot_state = "GESTURE CONTROL"

            start_gesture_camera()


        update_gesture_display(
            "IDLE"
        )

        update_robot()

        print(
            "GESTURE MODE"
        )

        return


    # ========================================================
    # MANUAL MODE
    # ========================================================

    if key == "m":

        if current_mode == MODE_GESTURE:

            stop_gesture_camera()


        current_mode = MODE_MANUAL

        robot_state = "MANUAL CONTROL"


        update_gesture_display(
            "IDLE"
        )


        print(
            "MANUAL MODE"
        )


        update_robot()

        return


    # ========================================================
    # AUTONOMOUS MODE
    # ========================================================

    if key == "a":

        if current_mode == MODE_GESTURE:

            stop_gesture_camera()


        current_mode = MODE_AUTONOMOUS

        robot_state = STATE_NAVIGATE

        avoidance_steps = 0


        path = calculate_path()

        path_index = 0


        draw_path()


        update_gesture_display(
            "IDLE"
        )


        print(
            "AUTONOMOUS MODE"
        )


        print(

            f"New route: "
            f"({robot.x:.2f}, {robot.y:.2f}) "
            f"-> "
            f"({target_x:.2f}, {target_y:.2f})"

        )


        distance_to_target = math.hypot(

            target_x - robot.x,
            target_y - robot.y

        )


        if distance_to_target < 0.12:

            robot_state = STATE_REACHED

        elif not path:

            robot_state = "NO PATH FOUND"


        update_robot()

        return


    # ========================================================
    # EMERGENCY STOP
    # ========================================================

    if key == " ":

        if current_mode == MODE_GESTURE:

            stop_gesture_camera()


        robot.stop_motors()

        current_mode = MODE_STOPPED

        robot_state = "EMERGENCY STOP"


        update_gesture_display(
            "IDLE"
        )


        print(
            "EMERGENCY STOP"
        )


        update_robot()

        return


    # ========================================================
    # RESET
    # ========================================================

    if key == "r":

        if current_mode == MODE_GESTURE:

            stop_gesture_camera()


        robot.reset()

        battery_level = 100.0

        dynamic_obstacle["active"] = False

        dynamic_patch.set_visible(False)

        current_mode = MODE_AUTONOMOUS

        robot_state = STATE_NAVIGATE

        avoidance_steps = 0


        path = calculate_path()

        path_index = 0


        draw_path()


        update_gesture_display(
            "IDLE"
        )


        print(
            "ROBOT RESET"
        )


        update_robot()

        return


    # ========================================================
    # MANUAL MOVEMENT
    # ========================================================

    if current_mode == MODE_MANUAL:

        manual_control(key)

        update_robot()


# ============================================================
# SIMULATION STEP
# ============================================================

def simulation_step():

    global battery_warning_visible
    global battery_warning_counter
    global current_mode
    global robot_state


    # ========================================================
    # CRITICAL BATTERY CHECK
    # ========================================================

    if battery_status() == "CRITICAL":

        robot.stop_motors()

        current_mode = MODE_STOPPED


        battery_warning_counter += 1


        if battery_warning_counter >= 5:

            battery_warning_visible = (
                not battery_warning_visible
            )

            battery_warning_counter = 0


        if battery_warning_visible:

            robot_state = (
                "CRITICAL BATTERY — ROBOT STOPPED"
            )

        else:

            robot_state = " "


        update_robot()

        return


    # ========================================================
    # NORMAL OPERATION
    # ========================================================

    if current_mode == MODE_AUTONOMOUS:

        autonomous_navigation()


    elif current_mode == MODE_GESTURE:

        process_gesture()


    update_robot()


# ============================================================
# LABELS
# ============================================================

ax.set_title(
    "Gesture-X | Autonomous Navigation & LiDAR"
)


ax.set_xlabel(
    "X Position"
)


ax.set_ylabel(
    "Y Position"
)


ax.legend(
    loc="upper left"
)


# ============================================================
# KEYBOARD EVENTS
# ============================================================

fig.canvas.mpl_connect(

    "key_press_event",

    on_key

)


# ============================================================
# START SIMULATION
# ============================================================

if __name__ == "__main__":

    update_robot()


    timer = fig.canvas.new_timer(
        interval=100
    )


    timer.add_callback(
        simulation_step
    )


    timer.start()


    plt.show()