def update_menu_state(key, menu_open):
    """
    Returns (menu_open, should_quit)
    ESC → open menu
    R   → resume
    Q   → quit
    """
    if not menu_open:
        if key == 27:  # ESC
            return True, False
        return False, False

    if key == ord('r'):
        return False, False
    elif key == ord('q'):
        return False, True

    return True, False