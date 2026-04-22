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
    update_target_mode
)
from serial_controller import SerialController
# Serial ----(UNCOMMENT TO ENABLE)
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

# Default target
target_mode = "heart"

while True:
    success, image = cap.read()
    if not success:
        break

    image = cv2.flip(image, 1)
    results = model(image, stream=True)

    h, w = image.shape[:2]
    center_x = w // 2
    center_y = h // 2

    draw_crosshair(image, center_x, center_y)

    target_found = False

    for r in results:
        boxes = r.boxes
        keypoints = r.keypoints

        for i, box in enumerate(boxes):
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            cls = int(box.cls[0])

            if cls == 0:  # person
                target_found = True
                draw_box_and_label(image, x1, y1, x2, y2)

                target_x, target_y = None, None
                heart_x, heart_y = None, None

                if keypoints is not None and len(keypoints) > i:
                    kps_xy, kps_conf = extract_keypoints(keypoints, i)

                    draw_keypoints_and_skeleton(
                        image,
                        kps_xy,
                        kps_conf,
                        config.SKELETON,
                        config.KP_CONF_THRES
                    )

                    heart_x, heart_y, x_sh, y_sh, x_hip, y_hip= compute_heart(
                        kps_xy,
                        kps_conf,
                        config.CONF_TH
                    )

                    if heart_x is not None:
                        draw_heart(
                            image,
                            heart_x,
                            heart_y,
                            x_sh,
                            y_sh,
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

        if target_found:
            break

    draw_mode(image, target_mode)

    command = f'{pan},{tilt}\n'
    # ser.write(command.encode())
    print(command.strip())

    cv2.imshow("Laser Tracker", image)
    key = cv2.waitKey(1)

    if key == 27:
        break

    target_mode = update_target_mode(key, target_mode)

cap.release()
cv2.destroyAllWindows()
# Graceful serial shutdown
# serial_ctrl.stop()