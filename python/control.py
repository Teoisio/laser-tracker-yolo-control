def compute_error(center_x, center_y, torso_x, torso_y):
    e_x = center_x - torso_x
    e_y = center_y - torso_y
    return e_x, e_y

def update_control(pan, tilt, e_x, e_y, Kc):
    pan = int(pan - Kc * e_x)
    tilt = int(tilt + Kc * e_y)
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

def limit_step(prev_pan, prev_tilt, pan, tilt, max_step_pan, max_step_tilt):
    pan  = int(max(prev_pan  - max_step_pan,  min(prev_pan  + max_step_pan,  pan)))
    tilt = int(max(prev_tilt - max_step_tilt, min(prev_tilt + max_step_tilt, tilt)))
    return pan, tilt

def update_selected_person(key, selected_person_index, num_people):
    if num_people == 0:
        return 0
    if key == ord('a'):
        return (selected_person_index - 1) % num_people
    elif key == ord('d'):
        return (selected_person_index + 1) % num_people
    return selected_person_index