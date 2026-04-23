import cv2
import numpy as np


def mouse_to_servo(mouse_x, mouse_y, frame_w, frame_h):
    """Map mouse pixel position to servo angles."""
    pan  = int(np.interp(mouse_x, [0, frame_w], [0, 180]))
    tilt = int(np.interp(mouse_y, [0, frame_h], [0, 180]))
    return pan, tilt


class MouseController:
    """
    Tracks mouse position and right-click state on an OpenCV window.
    - Right click once  → toggle laser
    - Mouse move        → update pan/tilt in manual mode
    """

    def __init__(self, window_name):
        self.window_name = window_name
        self.x = 0
        self.y = 0
        self.laser_on = False
        cv2.setMouseCallback(window_name, self._callback)

    def _callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_MOUSEMOVE:
            self.x = x
            self.y = y
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.laser_on = not self.laser_on

    def get_servo_angles(self, frame_w, frame_h):
        return mouse_to_servo(self.x, self.y, frame_w, frame_h)