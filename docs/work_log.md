# Laser Target Tracker Project — Work Log

## 1. Goal
Build a real-time system that detects a person with computer vision and points a pan-tilt laser toward a selected target point on the body.  
The system uses Python for vision and control, and Arduino for servo actuation.

The final goal is to:
- detect a person in the camera frame
- define a target point on the body
- compute the error between frame center and target point
- move the servos so that the laser points toward that target

---

## 2. General System Architecture

The project is divided into two main parts:

### Python side
Python handles:
- camera acquisition
- YOLO inference
- body keypoint extraction
- target-point computation
- error computation
- control law (P controller)
- automatic tracking mode
- manual mouse-control mode
- serial communication with Arduino

### Arduino side
Arduino handles:
- receive serial commands
- move the servos
- optionally turn laser on/off

### Data flow

The system operates in two modes, selected by the user using the keyboard (SPACE key):

- Automatic mode: target point is obtained from YOLO pose detection
- Manual mode: target point is defined by mouse input

The processing pipeline is:

camera frame  
→ user input (keyboard + mouse)  
→ mode selection (SPACE key)  
→ (optional) YOLO pose estimation  
→ target point generation (vision or mouse)  
→ error computation (center − target)  
→ control law (P controller)  
→ serial communication  
→ Arduino  
→ servo actuation

---

## 3. Control System

The control system is based on visual feedback.

### Input
The control input is the pair of reference angles sent to the two servos:
- pan
- tilt

### Output
The controlled output is not directly an angle, but the image position of the target point:
- target_x
- target_y

### Reference
The desired reference is the center of the frame:
- center_x
- center_y

### Error
The error is defined as the difference between frame center and target point:

- e_x = center_x - target_x
- e_y = center_y - target_y

This means:
- if the target is not centered, the controller changes the servo angles
- when the target reaches the frame center, the error tends to zero

### Controller
For now I am using a proportional controller:

- pan = pan - Kc * e_x
- tilt = tilt - Kc * e_y

This is simple and works, but the laser point still oscillates because the visual measurement is noisy.  
For this reason, future improvements may include smoothing, dead zone, or a more advanced controller.

Detailed control calculations and theoretical notes are stored separately here:

[Control theory notes](https://onedrive.live.com/personal/52385e9db3d3e4c5/_layouts/15/Doc.aspx?sourcedoc={b3d3e4c5-5e9d-2038-8052-700000000000}&action=edit&wd=target%28Final%20project.one%7C89c03916-2ec3-6b43-b4bd-f99d69b3e672%2FLaser%20Tracker%20Teoria%7C1370b02f-f1fb-0342-b154-0670466f73ca%2F%29&wdorigin=NavigationUrl)

---

## 4. Detection

At the beginning I used the `yolov8n.pt` model.  
In that version I detected the person with a bounding box and used the center of the rectangle as the target point.

The workflow was:
- detect person
- draw bounding box with `cv2` and `cvzone`
- compute rectangle center
- use rectangle center as the target

This method was simple, but precision was low and the laser point moved too much.  
The center of the box was not stable, because the box changes slightly from frame to frame.

For this reason I changed approach and used the `yolo11n-pose.pt` model.

This model detects:
- the person
- the 17 COCO body keypoints

That made it possible to define target points using body anatomy instead of only the bounding box.

---

## 5. Target Definition

The key problem was that YOLO pose detects body keypoints, but it does not directly provide a “heart” point.

So I defined a custom target point called **heart**.

### Why I introduced heart
I wanted a point that is:
- more stable than the bounding-box center
- more central than a shoulder
- still available even when some body parts are missing

### First heart idea
Initially the heart point was based only on shoulders:
- midpoint between left shoulder and right shoulder
- then a vertical offset downward

This already worked better than the box center.

### Improved heart computation
Later I improved the logic.

Current logic:
- if shoulders are missing → no valid heart point
- if shoulders exist and hips also exist:
  - compute shoulder midpoint
  - compute hip midpoint
  - compute a point along the torso axis
  - place the heart slightly above the torso center
- if shoulders exist but hips do not:
  - use fallback based on shoulder midpoint
  - estimate heart position using shoulder width

This makes the target more anatomically meaningful and more robust.

### Current heart computation summary
- midpoint between shoulders
- if hips available → refined using torso axis
- fallback → shoulder-based offset

### Other selectable target points
Besides heart, the system can also point to:
- nose
- left shoulder
- right shoulder
- left hip
- right hip

The default target is currently **heart**.

---

## 6. Serial Communication

Python sends commands to Arduino using serial communication.

### Message format
Python sends:
`pan,tilt\n`

Example:
`90,60\n`

### Arduino behavior
Arduino:
- reads the incoming string
- finds the comma
- extracts pan and tilt values
- constrains them in a safe range
- writes them to the servo motors

This communication allows Python to run the vision/control loop while Arduino executes the physical motion.

---

## 7. Arduino Logic

On Arduino I use:
- `Servo.h`
- one servo for pan
- one servo for tilt
- one laser output pin

### Automatic mode
In automatic mode:
- Arduino reads pan/tilt values from serial
- it moves the servos accordingly

### Manual mode
In manual mode:
- mouse controls the pan-tilt

This is useful for testing and alignment.

---

## 8. File Structure

The code is modularized so that each file has a specific responsibility.

### `main.py`
This is the main loop of the project.

It:
- reads frames from the camera
- runs the YOLO model
- gets boxes and keypoints
- computes the selected target point
- computes the control error
- updates pan and tilt
- sends commands to serial
- draws the interface on screen
- reads keyboard input to change target mode

So `main.py` is the orchestrator of the whole system.

### `config.py`
Contains project parameters such as:
- camera index
- frame width and height
- model path
- gain `Kc`
- initial pan/tilt values
- confidence thresholds
- skeleton connections

This file is useful because all constants are centralized in one place.

### `vision.py`
Contains vision-related logic.

It includes functions for:
- extracting keypoints from YOLO results
- checking whether a keypoint is valid
- computing the custom heart point
- selecting which target point should be used

This file handles the geometry of the body targets.

### `drawing.py`
Contains all the drawing/visualization functions.

It is used to:
- draw frame crosshair
- draw bounding boxes
- draw skeleton and keypoints
- draw heart point
- draw target mode
- draw the error text

This file keeps graphics separate from logic.

### `control.py`
Contains control-related functions.

It includes:
- error computation
- proportional update of pan and tilt
- application of angle limits
- keyboard-based target mode update

This file handles the decision and control part.

### `serial_controller.py`
This file manages serial communication in a cleaner way.

Its purpose is:
- to decouple the vision loop from serial writes
- to send only the latest pan/tilt command
- to avoid blocking the main loop

This is useful because the camera loop can run faster and more smoothly.

### `arduino/pan_tilt_laser_tracker/pan_tilt_laser_tracker.ino`
This is the Arduino sketch.

It:
- receives serial commands
- controls the two servos
- allows manual mode with joystick
- controls the laser pin

---

## 9. Main Program Flow (`main.py`)

The sequence inside `main.py` is approximately:

1. Open camera
2. Load YOLO pose model
3. Initialize pan and tilt values
4. Set default target mode (`heart`)
5. Start loop:
   - read a frame
   - flip image
   - run YOLO
   - compute frame center
   - draw crosshair
   - search for first detected person
   - extract pose keypoints
   - compute heart point
   - select current target point
   - draw target
   - compute error
   - update controller
   - apply limits
   - send command
   - show interface
   - read keyboard input
6. Exit loop when ESC is pressed
7. Close camera and windows
8. stop serial communication cleanly if enabled

This section is important because it explains how all files interact.

---

## 10. Current State of the Project

At the moment the project already includes:
- person detection
- pose estimation
- custom heart target computation
- multiple target modes
- proportional controller
- modular Python architecture
- Arduino integration
- manual/automatic mode on Arduino

So the basic full system is already working conceptually.

---

## 11. Main Problems Observed

The main practical issue is that the laser point does not remain perfectly still on the target.

Possible causes:
- noisy keypoint detection
- frame-by-frame fluctuations
- no smoothing yet
- proportional control only
- servo mechanical limitations

This is the main aspect to improve next.

---

## 12. TODO / Next Steps

### Documentation
- [ ] update `README.md`
- [ ] write `control_design.pdf`
- [ ] write `report.pdf`

### Python / Vision
- [ ] smooth the critical keypoints
- [ ] add more selectable target points
- [ ] improve handling of missing keypoints

### Interface
- [ ] when pressing TAB, show a control/help panel
- [ ] when pressing ESC, show an exit panel
- [ ] add command legend on screen
- [ ] implement close-laser shortcut

### Control
- [ ] add smoothing
- [ ] maybe add dead zone
- [ ] maybe add max servo-step limitation

### Interaction modes
- [ ] add mouse-control mode
- [ ] allow switching between automatic and mouse control

### Model / Recognition
- [ ] investigate custom training or custom identification
- [ ] example idea: distinguish specific people

### Hardware
- [ ] wait for servos
- [ ] complete assembly and wiring
- [ ] test real setup

---

## 13. Notes for Final Report
This work log is only for remembering the development process.

Later I will:
- correct language
- improve structure
- make diagrams
- add images and screenshots
- make the report more formal and publishable