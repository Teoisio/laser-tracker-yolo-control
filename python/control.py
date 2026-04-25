def compute_error(center_x, center_y, torso_x, torso_y):
    e_x = center_x - torso_x
    e_y = center_y - torso_y
    return e_x, e_y

def update_control(pan, tilt, e_x, e_y, Kc):
    pan = int(pan - Kc * e_x)
    tilt = int(tilt - Kc * e_y)
    return pan, tilt

def apply_limits(pan, tilt):
    pan = max(0, min(180, pan))
    tilt = max(0, min(180, tilt))
    return pan, tilt

def update_target_mode(key, current_mode):
    if key == ord('0'):
        return "heart"
    elif key == ord('1'):
        return "nose"
    elif key == ord('2'):
        return "left_shoulder"
    elif key == ord('3'):
        return "right_shoulder"
    elif key == ord('4'):
        return "left_hip"
    elif key == ord('5'):
        return "right_hip"
    else:
        return current_mode
    
def update_tracking_mode(key, current_mode):
    if key == ord(' '):
        return "manual" if current_mode == "auto" else "auto"
    return current_mode

def apply_dead_zone(e_x, e_y, threshold):
    if abs(e_x) < threshold:
        e_x = 0
    if abs(e_y) < threshold:
        e_y = 0
    return e_x, e_y