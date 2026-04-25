ARROW_LEFT  = 2
ARROW_RIGHT = 3
ARROW_UP    = 0
ARROW_DOWN  = 1

SETTING_KEYS = ['dead_zone', 'Kc', 'max_step_pan', 'max_step_tilt']

SETTINGS_STEP = {
    'dead_zone':     1,
    'Kc':            0.005,
    'max_step_pan':  1,
    'max_step_tilt': 1,
}

SETTINGS_LIMITS = {
    'dead_zone':     (0, 50),
    'Kc':            (0.001, 0.2),
    'max_step_pan':  (1, 20),
    'max_step_tilt': (1, 20),
}


def update_menu_state(key, menu_open):
    """
    ESC → open menu
    R   → resume
    Q   → quit
    Returns (menu_open, should_quit)
    """
    if not menu_open:
        if key == 27:
            return True, False
        return False, False

    if key == ord('r'):
        return False, False
    elif key == ord('q'):
        return False, True

    return True, False


def update_settings(key, settings, selected_setting):
    """
    UP / DOWN        → navigate between settings
    LEFT / RIGHT     → decrease / increase selected value
    Returns (settings, selected_setting)
    """
    if key == ARROW_UP:
        selected_setting = (selected_setting - 1) % len(SETTING_KEYS)

    elif key == ARROW_DOWN:
        selected_setting = (selected_setting + 1) % len(SETTING_KEYS)

    elif key == ARROW_LEFT or key == ARROW_RIGHT:
        k = SETTING_KEYS[selected_setting]
        delta = SETTINGS_STEP[k] * (1 if key == ARROW_RIGHT else -1)
        lo, hi = SETTINGS_LIMITS[k]
        settings[k] = round(max(lo, min(hi, settings[k] + delta)), 4)

    return settings, selected_setting