def valid(idx, kps_conf, conf_th):
    if kps_conf is None:
        return True
    return kps_conf[idx] > conf_th

def extract_keypoints(keypoints, i):
    kps_xy = keypoints.xy[i].cpu().numpy()
    kps_conf = None
    if keypoints.conf is not None:
        kps_conf = keypoints.conf[i].cpu().numpy()
    return kps_xy, kps_conf

def compute_heart(kps_xy, kps_conf, conf_th):
    has_shoulders = valid(5, kps_conf, conf_th) and valid(6, kps_conf, conf_th)
    has_hips = valid(11, kps_conf, conf_th) and valid(12, kps_conf, conf_th)

    if not has_shoulders:
        return None, None, None, None, None, None

    x_ls, y_ls = kps_xy[5]
    x_rs, y_rs = kps_xy[6]
    x_sh = (x_ls + x_rs) / 2
    y_sh = (y_ls + y_rs) / 2

    if has_hips:
        x_lh, y_lh = kps_xy[11]
        x_rh, y_rh = kps_xy[12]
        x_hip = (x_lh + x_rh) / 2
        y_hip = (y_lh + y_rh) / 2

        heart_x = int((x_sh + x_hip) / 2)
        heart_y = int((y_sh + y_hip) / 2 - 0.1 * (y_hip - y_sh))
    else:
        shoulder_width = abs(x_rs - x_ls)
        x_hip = x_sh
        y_hip = y_sh + 0.25 * shoulder_width

        heart_x = int(x_sh)
        heart_y = int(y_hip)

    return heart_x, heart_y, x_sh, y_sh, x_hip, y_hip
    
def select_target_point(target_mode, kps_xy, kps_conf, torso_x, torso_y, conf_th):
    if target_mode == "heart":
        if torso_x is not None:
            return torso_x, torso_y

    elif target_mode == "nose":
        if valid(0, kps_conf, conf_th):
            return int(kps_xy[0][0]), int(kps_xy[0][1])

    elif target_mode == "left_shoulder":
        if valid(5, kps_conf, conf_th):
            return int(kps_xy[5][0]), int(kps_xy[5][1])

    elif target_mode == "right_shoulder":
        if valid(6, kps_conf, conf_th):
            return int(kps_xy[6][0]), int(kps_xy[6][1])

    elif target_mode == "left_hip":
        if valid(11, kps_conf, conf_th):
            return int(kps_xy[11][0]), int(kps_xy[11][1])

    elif target_mode == "right_hip":
        if valid(12, kps_conf, conf_th):
            return int(kps_xy[12][0]), int(kps_xy[12][1])

    return None, None

def get_person_indices(boxes):
    return [i for i, box in enumerate(boxes) if int(box.cls[0]) == 0]

def sort_people_by_x(boxes, person_indices):
    def center_x(i):
        xyxy = boxes.xyxy[i]
        if len(xyxy) < 4:
            return float('inf')
        return (xyxy[0] + xyxy[2]) / 2
    return sorted(person_indices, key=center_x)

def select_person_index(person_indices, selected_person_index):
    if not person_indices:
        return None
    selected_person_index = min(selected_person_index, len(person_indices) - 1)
    return person_indices[selected_person_index]