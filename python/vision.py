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
    if valid(5, kps_conf, conf_th) and valid(6, kps_conf, conf_th):
        x_ls, y_ls = kps_xy[5]
        x_rs, y_rs = kps_xy[6]

        x_sh = (x_ls + x_rs) / 2
        y_sh = (y_ls + y_rs) / 2

        shoulder_width = abs(x_rs - x_ls)

        offset = 0.25 * shoulder_width

        heart_x = int(x_sh)
        heart_y = int(y_sh + offset)

        return heart_x, heart_y, x_sh, y_sh

    return None, None, None, None
    
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