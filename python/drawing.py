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

def draw_person_id(image, x1, y1, person_number, selected=False):
    label = f"SELECTED {person_number}" if selected else f"Person {person_number}"
    color = (0, 0, 255) if selected else (255, 0, 0)
    cvzone.putTextRect(image, label, (max(0, x1), max(30, y1)), colorR=color)

def draw_selected_person_status(image, selected_person_index, num_people):
    cv2.putText(
        image,
        f"Selected person: {selected_person_index+1} / {num_people}",
        (20, 120),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 200, 255),
        2
    )

def draw_esc_menu(image):
    h, w = image.shape[:2]

    # Semi-transparent dark overlay
    overlay = image.copy()
    cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.5, image, 0.5, 0, image)

    cx = w // 2

    cv2.putText(image, "PAUSED", (cx - 100, h // 2 - 120),
                cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
    cv2.putText(image, "R  -  Resume", (cx - 120, h // 2 - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(image, "Q  -  Quit", (cx - 120, h // 2 + 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(image, "Future settings:", (cx - 120, h // 2 + 120),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (180, 180, 180), 1)
    cv2.putText(image, "1 - Dead zone   2 - Max step   3 - Gain",
                (cx - 220, h // 2 + 160),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (140, 140, 140), 1)