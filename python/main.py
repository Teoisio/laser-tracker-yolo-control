import cv2
from ultralytics import YOLO

import config
from drawing import (
    draw_crosshair,
    draw_box_and_label,
    draw_keypoints_and_skeleton,
    draw_heart,
    draw_error,
    draw_mode
)
from vision import (
    extract_keypoints,
    compute_heart,
    select_target_point
)
from control import (
    compute_error,
    update_control,
    apply_limits,
    update_target_mode,
    update_tracking_mode
)
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

# Mouse controller (initialized after first imshow)
mouse_ctrl = None

keypoint_smoother = KeypointSmoother(
    alpha=config.SMOOTHER_ALPHA,
    conf_th=config.KP_CONF_THRES
)
while True:
    success, image = cap.read()
    if not success:
        break

    image = cv2.flip(image, 1)

    h, w = image.shape[:2]
    center_x = w // 2
    center_y = h // 2

    draw_crosshair(image, center_x, center_y)

    if tracking_mode == "auto":
        results = model(image, stream=True)

        for r in results:
            boxes = r.boxes
            keypoints = r.keypoints

            for i, box in enumerate(boxes):
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                cls = int(box.cls[0])

                if cls == 0:  # person
                    draw_box_and_label(image, x1, y1, x2, y2)

                    target_x, target_y = None, None
                    heart_x, heart_y = None, None

                    if keypoints is not None and len(keypoints) > i:
                        
                        kps_xy, kps_conf = extract_keypoints(keypoints, i)
                        
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
                            draw_heart(
                                image,
                                heart_x, heart_y,
                                x_sh, y_sh,
                                x_hip, y_hip
                            )

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
                        draw_error(image, e_x, e_y)
                        pan, tilt = update_control(pan, tilt, e_x, e_y, config.Kc)

                    pan, tilt = apply_limits(pan, tilt)

                    break

            else:
                continue
            break

    elif tracking_mode == "manual" and mouse_ctrl is not None:
        pan, tilt = mouse_ctrl.get_servo_angles(w, h)
        pan, tilt = apply_limits(pan, tilt)

    draw_mode(image, f"{tracking_mode} | {target_mode}")

    cv2.imshow("Laser Tracker", image)

    # Init mouse controller after window is created
    if mouse_ctrl is None:
        mouse_ctrl = MouseController("Laser Tracker")

    laser = int(mouse_ctrl.laser_on) if mouse_ctrl else 0

    # Push latest state to serial thread (non-blocking)
    # serial_ctrl.update(pan, tilt, laser)
    print(f'{pan},{tilt},{laser}')  # debug — remove when serial is active

    key = cv2.waitKey(1)

    if key == 27:  # ESC
        break

    target_mode = update_target_mode(key, target_mode)
    tracking_mode = update_tracking_mode(key, tracking_mode)

cap.release()
cv2.destroyAllWindows()
# serial_ctrl.stop()