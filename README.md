# Gesture-X

## Computer Vision-Based Robotic Navigation and Gesture Control

Gesture-X is a Python-based robotic navigation and control system that integrates computer vision, hand gesture recognition, LiDAR-inspired sensing, A* path planning, obstacle avoidance, battery management, and multiple control modes into a single platform.

The system supports autonomous navigation toward a target, keyboard-based manual control, and real-time hand gesture control through a camera interface. Safety mechanisms continuously monitor the robot's surroundings and prevent movement when obstacles or environment boundaries are detected.

## Live Demo

**Live Demo:** [View Gesture-X Demo](YOUR_LIVE_DEMO_LINK_HERE)

The demonstration showcases autonomous navigation, A* path planning, LiDAR-inspired obstacle detection, real-time telemetry, and camera-based hand gesture control.

## Key Features

### Gesture-Based Robot Control

Gesture-X uses MediaPipe hand tracking and computer vision to provide a natural human-robot interaction interface.

Supported commands include:

* Move forward
* Move backward
* Turn left
* Turn right
* Stop

Detected gestures and their corresponding robot commands are displayed in real time.

### Autonomous Navigation

The autonomous navigation system uses the A* search algorithm to generate a path from the robot's current position to a defined target.

The navigation system:

1. Generates a route using A* path planning.
2. Follows the generated waypoints.
3. Continuously monitors the environment.
4. Detects obstacles along the route.
5. Stops when movement is blocked.
6. Performs obstacle avoidance.
7. Recalculates the route when necessary.

### Obstacle and Boundary Detection

A simulated multi-directional LiDAR system provides distance measurements around the robot.

The system detects:

* Static obstacles
* Dynamic obstacles
* Front and rear obstacles
* Environment boundaries
* Directional movement restrictions

Obstacle detection is integrated into autonomous, manual, and gesture-based control modes.

### Manual Control

The robot can be controlled through keyboard input.

| Key         | Function       |
| ----------- | -------------- |
| Up Arrow    | Move Forward   |
| Down Arrow  | Move Backward  |
| Left Arrow  | Turn Left      |
| Right Arrow | Turn Right     |
| Space       | Emergency Stop |

Movement commands are checked against sensor readings before execution to prevent the robot from moving into detected obstacles or boundaries.

### Battery and Power Management

Gesture-X includes a simulated battery management system that tracks power consumption based on robot movement and turning.

The system provides three power states:

* Normal
* Low Battery
* Critical Battery

When the battery reaches the critical threshold, the robot automatically stops and enters a safe stopped state.

### Real-Time Telemetry

The visualization dashboard provides real-time information about the robot and navigation system, including:

* Robot position
* Robot heading
* Target position
* A* route
* Current waypoint
* Speed level
* LiDAR sensor readings
* Current control mode
* Gesture status
* Robot command
* Navigation state
* Battery percentage
* Power status

## System Architecture

```text
                   Camera Input
                        |
                        v
              Hand Tracking / MediaPipe
                        |
                        v
              Gesture Classification
                        |
                        v
                Gesture Controller
                        |
                        v
        +---------------+---------------+
        |               |               |
        v               v               v
   Manual Control   Autonomous      Gesture Control
                        |               |
                        +-------+-------+
                                |
                                v
                        Robot Controller
                                |
                 +--------------+--------------+
                 |                             |
                 v                             v
          LiDAR-Inspired Sensing        Battery Management
                 |
                 v
          Obstacle Detection
                 |
                 v
            A* Path Planner
                 |
                 v
              Target
```

## Navigation and Control

Gesture-X follows a perception-planning-control architecture.

```text
Perception
    |
    v
Sensor Measurements
    |
    v
Environment Analysis
    |
    v
Path Planning / Control Decision
    |
    v
Robot Motion
    |
    v
Continuous Sensor Feedback
```

This allows the system to continuously evaluate the robot's surroundings rather than treating navigation as a single predetermined movement sequence.

## Differential Drive Model

The robot is modeled as a differential-drive system with independent left and right wheel velocities.

The model calculates:

* Linear velocity
* Angular velocity
* Robot heading
* Position updates

This provides a foundation for extending the simulation to physical differential-drive hardware.

## LiDAR-Inspired Sensing

The simulated sensor system casts multiple directional rays around the robot and calculates the distance to the nearest obstacle or environment boundary.

Sensor directions include:

* Front
* Front-left
* Front-right
* Left
* Right
* Back
* Back-left

These measurements are used by the navigation and safety layers to determine whether movement is permitted.

## A* Path Planning

A* is used to determine a route between the robot's current position and its target while accounting for known obstacles.

When an obstacle affects the planned route, the navigation system can stop the robot and recalculate the path using the updated environment.

## Control Modes

### Autonomous Mode

Press `A`.

The robot automatically plans and follows a route toward the target while monitoring obstacles and boundaries.

### Manual Mode

Press `M`.

The robot responds to keyboard commands while maintaining obstacle and boundary protection.

### Gesture Mode

Press `G`.

The system activates the camera and interprets hand gestures using MediaPipe.

### Emergency Stop

Press `Space`.

The robot immediately stops and enters the emergency-stop state.

### Reset

Press `R`.

The robot returns to its initial position and resets the simulation state and battery level.

## Speed Control

Five configurable speed levels are available.

| Key | Speed |
| --- | ----: |
| 1   |   25% |
| 2   |   50% |
| 3   |   75% |
| 4   |  100% |
| 5   |  125% |

## Technology Stack

| Technology               | Purpose                              |
| ------------------------ | ------------------------------------ |
| Python                   | Core application and control logic   |
| OpenCV                   | Camera input and computer vision     |
| MediaPipe                | Real-time hand tracking              |
| Matplotlib               | Robotics visualization and telemetry |
| A*                       | Path planning                        |
| NumPy                    | Numerical computation                |
| Differential Drive Model | Robot motion simulation              |

## Project Structure

```text
Gesture-X/
|
├── main.py
├── requirements.txt
├── .gitignore
|
├── models/
│   └── hand_landmarker.task
|
└── src/
    |
    ├── control/
    │   ├── controller.py
    │   ├── gesture_robot.py
    │   ├── motor_controller.py
    │   └── pid_controller.py
    |
    ├── dashboard/
    │   └── app.py
    |
    ├── energy/
    │   └── battery.py
    |
    ├── gesture/
    │   └── gesture_detector.py
    |
    ├── navigation/
    │   └── planner.py
    |
    ├── robot/
    │   ├── command_interface.py
    │   └── robot.py
    |
    └── vision/
        ├── gesture_classifier.py
        ├── gesture_controller.py
        ├── gesture_test.py
        └── hand_tracker.py
```

## Installation

Clone the repository:

```bash
git clone https://github.com/anushkaahsan2931/Gesture-X.git
cd Gesture-X
```

Create and activate a virtual environment:

```bash
python3 -m venv .visionenv
source .visionenv/bin/activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the Project

Start the application with:

```bash
python main.py
```

For Gesture Mode, ensure that camera access is enabled for Python or the application environment.

## Keyboard Shortcuts

| Key           | Function        |
| ------------- | --------------- |
| `A`           | Autonomous Mode |
| `M`           | Manual Mode     |
| `G`           | Gesture Mode    |
| `R`           | Reset           |
| `Space`       | Emergency Stop  |
| `1-5`         | Speed Control   |
| `Up Arrow`    | Forward         |
| `Down Arrow`  | Backward        |
| `Left Arrow`  | Left            |
| `Right Arrow` | Right           |

## Project Objectives

Gesture-X was developed to explore the integration of computer vision, robotic navigation, and human-robot interaction within a single system.

The project focuses on the interaction between:

* Perception
* Path planning
* Decision making
* Motion control
* Human input
* Safety monitoring
* Real-time system feedback

A key component of the project is the integration of hand gestures as an alternative control interface, allowing a user to interact with the robot without relying exclusively on traditional keyboard controls.

## Future Development

Potential extensions include:

* Physical LiDAR integration
* Wheel encoder feedback
* ROS/ROS2 integration
* SLAM-based mapping
* Real-time camera-based obstacle detection
* Hardware deployment
* Improved trajectory tracking
* PID-based motion control
* Web-based telemetry
* Expanded gesture recognition

## Author

**Anushka Ahsan**

Electrical Engineering
Robotics | Computer Vision | Embedded Systems | Control Systems

## Repository

GitHub: [Gesture-X](https://github.com/anushkaahsan2931/Gesture-X)
