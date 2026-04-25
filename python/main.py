import cv2
from ultralytics import YOLO

import config
from drawing import (
    draw_crosshair,
    draw_keypoints_and_skeleton,
    draw_heart,
    draw_error,
    draw_mode,
    draw_person_id,
    draw_selected_person_status,
    draw_esc_menu
)
from vision import (
    extract_keypoints,
    compute_heart,
    select_target_point,
    get_person_indices,
    sort_people_by_x,
    select_person_index
)
from control import (
    compute_error,
    update_control,
    apply_limits,
    apply_dead_zone,
    limit_step,
    update_target_mode,
    update_tracking_mode,
    update_selected_person
)
from menu import update_menu_state

from smoother import KeypointSmoother

from mouse import MouseController

# from serial_controller import SerialController

# Serial --- (UNCOMMENT TO ENABLE)
# serial_ctrl = SerialController(port=config.SERIAL_PORT, baud=config.SERIAL_BAUD, interval=config.SERIAL_INTERVAL)
# serial_ctrl.start()

# Camera
cap = cv2.VideoCapture(config.CAMERA_INDEX)
cap.set(3, config.FRAME_WIDTH)
cap.set(4, config.FRAME_HEIGHT)

# Model
model = YOLO(config.MODEL_PATH)

# Initial servo angles
pan = config.PAN_INIT
tilt = config.TILT_INIT

# Default modes
target_mode = "heart"
tracking_mode = "auto"

# Multi-person tracking state
selected_person_index = 0
num_people = 0

# Menu state
menu_open = False
should_quit = False

# Mouse controller (initialized after first imshow)
mouse_ctrl = None

# Keypoint smoother
keypoint_smoother = KeypointSmoother(
    alpha=config.SMOOTHER_ALPHA,
    conf_th=config.KP_CONF_THRES
)

while True:
    num_people = 0

    success, image = cap.read()
    if not success:
        break

    image = cv2.flip(image, 1)

    h, w = image.shape[:2]
    center_x = w // 2
    center_y = h // 2

    draw_crosshair(image, center_x, center_y)

    if not menu_open:
        if tracking_mode == "auto":
            results = model(image, stream=True)

            for r in results:
                boxes = r.boxes
                keypoints = r.keypoints

                # Get all people sorted left to right
                person_indices = get_person_indices(boxes)
                person_indices = sort_people_by_x(boxes, person_indices)
                num_people = len(person_indices)

                # Clamp selected index in case people disappear
                selected_person_index = min(selected_person_index, max(0, num_people - 1))

                # Draw all detected people
                for rank, i in enumerate(person_indices):
                    x1, y1, x2, y2 = [int(v) for v in boxes.xyxy[i]]
                    color = (0, 0, 255) if rank == selected_person_index else (255, 0, 0)
                    cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
                    draw_person_id(
                        image,
                        x1,
                        y1,
                        rank + 1,
                        selected=(rank == selected_person_index)
                    )

                # Process only the selected person
                active_i = select_person_index(person_indices, selected_person_index)

                if active_i is not None:
                    target_x, target_y = None, None
                    heart_x, heart_y = None, None

                    if keypoints is not None and len(keypoints) > active_i:
                        kps_xy, kps_conf = extract_keypoints(keypoints, active_i)
                        kps_xy = keypoint_smoother.update(kps_xy, kps_conf)

                        draw_keypoints_and_skeleton(
                            image,
                            kps_xy,
                            kps_conf,
                            config.SKELETON,
                            config.KP_CONF_THRES
                        )

                        heart_x, heart_y, x_sh, y_sh, x_hip, y_hip = compute_heart(
                            kps_xy,
                            kps_conf,
                            config.CONF_TH
                        )

                        if heart_x is not None:
                            draw_heart(image, heart_x, heart_y, x_sh, y_sh, x_hip, y_hip)

                        target_x, target_y = select_target_point(
                            target_mode,
                            kps_xy,
                            kps_conf,
                            heart_x,
                            heart_y,
                            config.CONF_TH
                        )

                        if target_x is not None:
                            cv2.circle(image, (target_x, target_y), 5, (0, 0, 255), -1)
                            cv2.line(image, (center_x, center_y), (target_x, target_y), (0, 0, 255), 2)

                    if target_x is not None:
                        e_x, e_y = compute_error(center_x, center_y, target_x, target_y)
                        e_x, e_y = apply_dead_zone(e_x, e_y, config.DEAD_ZONE)
                        draw_error(image, e_x, e_y)

                        new_pan, new_tilt = update_control(pan, tilt, e_x, e_y, config.Kc)
                        pan, tilt = limit_step(pan, tilt, new_pan, new_tilt, config.MAX_STEP_PAN, config.MAX_STEP_TILT)

                    pan, tilt = apply_limits(pan, tilt)
                if num_people > 0:
                    draw_selected_person_status(image, selected_person_index, num_people)
                break  # only process first result

        elif tracking_mode == "manual" and mouse_ctrl is not None:
            pan, tilt = mouse_ctrl.get_servo_angles(w, h)
            pan, tilt = apply_limits(pan, tilt)

        if tracking_mode == "auto":
            draw_mode(image, f"auto | {target_mode}")
        else:
            draw_mode(image, "manual")

    if menu_open:
        draw_esc_menu(image)

    cv2.imshow("Laser Tracker", image)

    # Init mouse controller after window is created
    if mouse_ctrl is None:
        mouse_ctrl = MouseController("Laser Tracker")

    laser = int(mouse_ctrl.laser_on) if mouse_ctrl else 0

    # Push latest state to serial thread (non-blocking)
    # serial_ctrl.update(pan, tilt, laser)
    print(f'{pan},{tilt},{laser}')  # debug — remove when serial is active

    key = cv2.waitKey(1)

    menu_open, should_quit = update_menu_state(key, menu_open)
 
    if should_quit:
        break

    if not menu_open:
        target_mode = update_target_mode(key, target_mode)
        tracking_mode = update_tracking_mode(key, tracking_mode)

        # Update selected person and reset smoother if changed
        prev_selected = selected_person_index
        selected_person_index = update_selected_person(key, selected_person_index, num_people)
        if selected_person_index != prev_selected:
            keypoint_smoother.reset()

cap.release()
cv2.destroyAllWindows()
# serial_ctrl.stop()