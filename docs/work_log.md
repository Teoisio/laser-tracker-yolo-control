# Laser Target Tracker Project — Workflow

## 1. Overview

The system is a real-time vision-based tracker that controls a pan-tilt laser using Arduino.

It supports two operating modes:

- **Automatic mode** → target is obtained from YOLO pose detection  
- **Manual mode** → target is controlled by the mouse  

The system is divided into:

- Python → vision, control, user interaction  
- Arduino → actuation (servos + laser)

---

## 2. System Architecture

### Python side
Handles:

- camera acquisition  
- YOLO inference (pose model)  
- body keypoint extraction  
- target-point computation  
- error computation  
- control law (P controller)  
- manual mouse input  
- mode switching (keyboard)  
- serial communication  

---

### Arduino side
Handles:

- receiving `(pan, tilt, laser)` from serial  
- moving servos  
- controlling laser output  

Arduino acts only as an actuator controller.

---

## 3. Data Flow

The system operates in two modes selected by the user (SPACE key).

### Pipeline:

camera frame  
→ user input (keyboard + mouse)  
→ mode selection (automatic / manual)  

→ (if automatic) YOLO pose model  
→ keypoints  

→ target point generation (vision OR mouse)  
→ error computation  
→ control law  
→ serial command `(pan, tilt, laser)`  
→ Arduino  
→ servos + laser  

---

## 4. Modes

### 4.1 Automatic Mode

- YOLO pose model detects a person  
- Extracts 17 body keypoints  
- Computes a custom **heart target point**  
- Computes error relative to frame center  
- Updates pan and tilt using proportional control  

---

### 4.2 Manual Mode

- Mouse position defines the target  
- Mouse movement → mapped to servo angles  
- Right mouse click → toggles laser  

No YOLO computation is required in this mode.

---

### 4.3 Mode Switching

- SPACE key toggles:
  - "auto" ↔ "manual"

- ESC key exits the program

---

## 5. Target Definition

YOLO pose model provides 17 keypoints, but no direct “heart” point.

### Heart computation:

- midpoint between shoulders  
- if hips available → refined using torso axis  
- fallback → shoulder-based offset  

This produces a more stable and meaningful target compared to bounding box center.

---

## 6. Control System

### Reference:
- center of the frame

### Target:
- selected body point OR mouse position

### Error:

    e_x = center_x - target_x

    e_y = center_y - target_y

### Controller:

    Proportional controller:

        pan = pan - Kc * e_x

        tilt = tilt - Kc * e_y

### Limits:
Servo angles are constrained to safe ranges.

---

## 7. Serial Communication

### Message format: 
### pan,tilt,laser\n

Example: 
    90,60,1

### Behavior:

Python:
- computes latest values
- sends via serial thread

Arduino:
- parses values
- updates servos
- sets laser ON/OFF

---

## 8. Serial Controller (Threaded)

A background thread is used to:

- send commands at fixed intervals  
- avoid blocking the main loop  
- send only updated values  

This improves responsiveness and stability.

---

## 9. Mouse Control

Mouse interaction is handled using OpenCV callbacks.

### Features:

- mouse movement → updates `(pan, tilt)`  
- right click → toggles laser  

Mapping:
mouse_x → pan (0 → 180)
mouse_y → tilt (0 → 180)

---

## 10. Main Program Flow (main.py)

1. Initialize camera and model  
2. Initialize modes (`auto`, `heart`)  
3. Start loop:

   - capture frame  
   - flip image  
   - compute frame center  
   - draw crosshair  

   IF automatic mode:
   - run YOLO  
   - extract keypoints  
   - compute heart  
   - select target  
   - compute error  
   - update control  

   IF manual mode:
   - read mouse position  
   - map to servo angles  

   - apply limits  
   - compute laser state  
   - send `(pan, tilt, laser)`  

   - draw interface  
   - read keyboard input  

4. Exit on ESC  
5. release camera and close windows  

---

## 11. File Structure

### main.py
Main loop and system orchestration

### vision.py
- keypoint extraction  
- heart computation  
- target selection  

### control.py
- error computation  
- controller  
- mode switching  

### drawing.py
- visualization functions  

### mouse.py
- mouse tracking  
- mapping mouse → servo  
- laser toggle  

### serial_controller.py
- threaded serial communication  

### config.py
- parameters and constants  

### Arduino (.ino)
- receives serial data  
- controls servos and laser  

---

## 12. Current System Capabilities

- real-time person tracking  
- pose-based targeting  
- custom anatomical target (heart)  
- dual control mode (auto/manual)  
- mouse interaction  
- threaded serial communication  
- modular architecture  

---

## 13. Current Limitations

- target jitter due to noisy keypoints  
- proportional control only  
- no smoothing/filtering yet  
- no calibration between pixels and servo angles  

---

## 14. Next Steps (TODO)

### Vision
- [ ] smooth keypoints / target point  
- [ ] improve fallback logic  

### Control
- [ ] add dead zone  
- [ ] limit max servo speed  
- [ ] consider PI/PID  

### Interface
- [ ] add UI panel (TAB)  
- [ ] improve visualization  

### System
- [ ] full hardware testing  
- [ ] calibration  

### Documentation
- [ ] complete report  
- [ ] diagrams  
- [ ] demo video  

---

## 15. Notes

This file represents the development workflow and system logic.  
It will be refined later into a formal report.