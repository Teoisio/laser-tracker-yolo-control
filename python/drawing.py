import cv2
import cvzone


def draw_crosshair(image, center_x, center_y):
    cv2.circle(image, (center_x, center_y), 5, (0, 0, 255), -1)

def draw_box_and_label(image, x1, y1, x2, y2):
    cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0, 0), 2)
    cvzone.putTextRect(image, "Target", (max(0, x1), max(30, y1)))

def draw_keypoints_and_skeleton(image, kps_xy, kps_conf, skeleton, kp_conf_thres):
    # Draw points
    for j, (kx, ky) in enumerate(kps_xy):
        if kps_conf is None or kps_conf[j] > kp_conf_thres:
            cv2.circle(image, (int(kx), int(ky)), 5, (0, 255, 0), -1)

    # Draw skeleton lines
    for a, b in skeleton:
        if a < len(kps_xy) and b < len(kps_xy):
            if kps_conf is None or (kps_conf[a] > kp_conf_thres and kps_conf[b] > kp_conf_thres):
                xA, yA = kps_xy[a]
                xB, yB = kps_xy[b]
                cv2.line(
                    image,
                    (int(xA), int(yA)),
                    (int(xB), int(yB)),
                    (255, 255, 0),
                    2
                )

def draw_heart(image, heart_x, heart_y, x_sh, y_sh, x_hip, y_hip):
    cv2.line(image, (int(x_sh), int(y_sh)), (int(x_hip), int(y_hip)), (255, 255, 0), 2)
    cv2.circle(image, (int(heart_x), int(heart_y)), 5, (0, 255, 0), -1)

def draw_error(image, e_x, e_y):
    cv2.putText(
        image,
        f"e_x={e_x}, e_y={e_y}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 255),
        2
    )

def draw_mode(image, target_mode):
    cv2.putText(
        image,
        f"Target: {target_mode}",
        (20, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 0),
        2
    )