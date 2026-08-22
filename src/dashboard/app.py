import math
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# ============================================================

# PAGE CONFIG

# ============================================================

st.set_page_config(
page_title="Gesture-X | Robotics Dashboard",
page_icon="",
layout="wide"
)

# ============================================================

# TITLE

# ============================================================

st.title("Gesture-X")
st.subheader("Autonomous Robotic Navigation & Gesture Control")

st.markdown(
"""
Gesture-X is a computer vision-based robotic navigation and control
system integrating autonomous path planning, obstacle detection,
LiDAR-inspired sensing, differential-drive motion modeling,
battery management, and real-time hand gesture control.
"""
)

# ============================================================

# SIDEBAR

# ============================================================

st.sidebar.header("Robot Controls")

mode = st.sidebar.selectbox(
"Control Mode",
[
"Autonomous",
"Manual",
"Gesture"
]
)

speed = st.sidebar.slider(
"Speed",
25,
125,
100,
step=25
)

st.sidebar.divider()

st.sidebar.markdown("### System Features")

st.sidebar.markdown(
"""

* A* path planning
* Obstacle detection
* Boundary protection
* LiDAR-inspired sensing
* Gesture recognition
* Differential-drive model
* Battery monitoring
* Emergency-stop logic
  """
  )

# ============================================================

# ENVIRONMENT

# ============================================================

WIDTH = 10
HEIGHT = 8

robot_x = 2.0
robot_y = 2.0

target_x = 6.0
target_y = 6.5

heading = 35

obstacles = [
(4, 1, 1, 3),
(7, 4, 1, 3)
]

# ============================================================

# PATH

# ============================================================

path = [
(2.0, 2.0),
(2.0, 3.0),
(2.0, 4.0),
(3.0, 4.0),
(3.0, 5.0),
(4.0, 5.0),
(5.0, 5.0),
(5.0, 6.0),
(6.0, 6.5)
]

# ============================================================

# SIMULATED TELEMETRY

# ============================================================

battery = 87.4

front_distance = 1.42
front_left_distance = 1.18
front_right_distance = 1.65
left_distance = 2.0
right_distance = 1.72
back_distance = 1.95

distance_to_target = math.hypot(
target_x - robot_x,
target_y - robot_y
)

# ============================================================

# STATUS

# ============================================================

if mode == "Autonomous":
    robot_status = "NAVIGATING"
    navigation_state = "A* ROUTE ACTIVE"
elif mode == "Manual":
    robot_status = "MANUAL CONTROL"
    navigation_state = "USER CONTROL"
else:
    robot_status = "GESTURE CONTROL"
    navigation_state = "VISION INPUT ACTIVE"

# ============================================================

# TOP METRICS

# ============================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
st.metric(
"Battery",
f"{battery:.1f}%",
"NORMAL"
)

with col2:
st.metric(
"Position",
f"{robot_x:.1f}, {robot_y:.1f}"
)

with col3:
st.metric(
"Heading",
f"{heading}°"
)

with col4:
st.metric(
"Target Distance",
f"{distance_to_target:.2f} m"
)

# ============================================================

# MAIN DASHBOARD

# ============================================================

left, right = st.columns([2.2, 1])

# ============================================================

# ROBOT VISUALIZATION

# ============================================================

with left:

```
st.markdown("### Robotics Environment")

fig, ax = plt.subplots(
    figsize=(9, 6)
)

ax.set_xlim(0, WIDTH)
ax.set_ylim(0, HEIGHT)

ax.set_xlabel("X Position (m)")
ax.set_ylabel("Y Position (m)")

ax.set_title(
    "Gesture-X Navigation Environment"
)

ax.grid(
    True,
    linestyle=":",
    alpha=0.35
)

# --------------------------------------------------------
# Boundary
# --------------------------------------------------------

boundary = patches.Rectangle(
    (0.3, 0.3),
    9.4,
    7.4,
    fill=False,
    linewidth=2
)

ax.add_patch(boundary)

# --------------------------------------------------------
# Obstacles
# --------------------------------------------------------

for x, y, width, height in obstacles:

    obstacle = patches.Rectangle(
        (x, y),
        width,
        height,
        linewidth=2,
        fill=True,
        alpha=0.25
    )

    ax.add_patch(obstacle)

    for level in range(1, 3):

        shelf_y = y + (
            height * level / 3
        )

        ax.plot(
            [x, x + width],
            [shelf_y, shelf_y],
            linewidth=1
        )

# --------------------------------------------------------
# A* PATH
# --------------------------------------------------------

path_x = [
    point[0]
    for point in path
]

path_y = [
    point[1]
    for point in path
]

ax.plot(
    path_x,
    path_y,
    linestyle="--",
    linewidth=2,
    label="A* Route"
)

# --------------------------------------------------------
# TARGET
# --------------------------------------------------------

target_outer = patches.Circle(
    (target_x, target_y),
    0.38,
    fill=False,
    linewidth=2
)

target_inner = patches.Circle(
    (target_x, target_y),
    0.20,
    fill=False,
    linewidth=2
)

ax.add_patch(target_outer)
ax.add_patch(target_inner)

ax.text(
    target_x,
    target_y - 0.6,
    "TARGET",
    ha="center",
    fontsize=9
)

# --------------------------------------------------------
# ROBOT
# --------------------------------------------------------

robot = patches.Circle(
    (robot_x, robot_y),
    0.30,
    linewidth=2
)

ax.add_patch(robot)

# --------------------------------------------------------
# ROBOT HEADING
# --------------------------------------------------------

angle = math.radians(heading)

ax.plot(
    [
        robot_x,
        robot_x + 0.55 * math.cos(angle)
    ],
    [
        robot_y,
        robot_y + 0.55 * math.sin(angle)
    ],
    linewidth=3
)

# --------------------------------------------------------
# SENSOR RAYS
# --------------------------------------------------------

sensor_angles = [
    -90,
    -45,
    0,
    45,
    90,
    135,
    180
]

sensor_distances = [
    right_distance,
    front_right_distance,
    front_distance,
    front_left_distance,
    left_distance,
    back_distance,
    back_distance
]

for sensor_angle, distance in zip(
    sensor_angles,
    sensor_distances
):

    sensor_angle = math.radians(
        heading + sensor_angle
    )

    end_x = (
        robot_x
        + distance * math.cos(sensor_angle)
    )

    end_y = (
        robot_y
        + distance * math.sin(sensor_angle)
    )

    ax.plot(
        [robot_x, end_x],
        [robot_y, end_y],
        linestyle=":",
        linewidth=0.8,
        alpha=0.5
    )

ax.legend(
    loc="upper left"
)

st.pyplot(
    fig,
    use_container_width=True
)
```

# ============================================================

# TELEMETRY

# ============================================================

with right:

```
st.markdown("### System Status")

st.success(
    f"MODE: {mode.upper()}"
)

st.info(
    navigation_state
)

st.markdown("### Navigation")

st.write(
    f"Robot Position: ({robot_x:.2f}, {robot_y:.2f})"
)

st.write(
    f"Target Position: ({target_x:.2f}, {target_y:.2f})"
)

st.write(
    f"Distance to Target: {distance_to_target:.2f} m"
)

st.write(
    f"A* Waypoints: {len(path)}"
)

st.markdown("### LiDAR-Inspired Sensors")

st.write(
    f"Front: {front_distance:.2f} m"
)

st.write(
    f"Front-Left: {front_left_distance:.2f} m"
)

st.write(
    f"Front-Right: {front_right_distance:.2f} m"
)

st.write(
    f"Left: {left_distance:.2f} m"
)

st.write(
    f"Right: {right_distance:.2f} m"
)

st.write(
    f"Back: {back_distance:.2f} m"
)

st.markdown("### Power")

if battery <= 5:
    st.error("CRITICAL BATTERY")
elif battery <= 20:
    st.warning("LOW BATTERY")
else:
    st.success("BATTERY NORMAL")

st.progress(
    battery / 100
)
```

# ============================================================

# GESTURE CONTROL

# ============================================================

st.divider()

st.markdown("### Gesture Control")

gesture_col1, gesture_col2, gesture_col3, gesture_col4 = st.columns(4)

with gesture_col1:
st.write("Forward")
st.code("MOVE_FORWARD")

with gesture_col2:
st.write("Backward")
st.code("MOVE_BACKWARD")

with gesture_col3:
st.write("Left / Right")
st.code("TURN_LEFT / TURN_RIGHT")

with gesture_col4:
st.write("Stop")
st.code("STOP")

st.caption(
"Gesture-X uses computer vision and MediaPipe hand tracking "
"to translate recognized hand gestures into robot commands."
)

# ============================================================

# PROJECT INFORMATION

# ============================================================

st.divider()

st.markdown("### Technology Stack")

tech1, tech2, tech3, tech4, tech5 = st.columns(5)

with tech1:
st.write("Python")

with tech2:
st.write("OpenCV")

with tech3:
st.write("MediaPipe")

with tech4:
st.write("A* Path Planning")

with tech5:
st.write("Matplotlib")

st.markdown(
"""
**Gesture-X** demonstrates the integration of computer vision,
robotics, autonomous navigation, path planning, obstacle detection,
motion control, and human-robot interaction within a single system.
"""
)

st.markdown(
"[View the source code on GitHub](https://github.com/anushkaahsan2931/Gesture-X)"
)
