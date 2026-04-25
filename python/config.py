import cv2
from ultralytics import YOLO

#Serial
#SERIAL_PORT = /dev/cu.usbmodem1201
#SERIAL_BAUD = 115200
#SERIAL_INTERVAL = 0.05 

#Camera
CAMERA_INDEX = 0
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

#Model
MODEL_PATH = 'yolo11n-pose.pt'

#Gain
Kc = 0.05

#Initial servo angles
PAN_INIT = 90
TILT_INIT = 90

# COCO 17-keypoint skeleton connections
# 0 nose
# 1 left eye, 2 right eye
# 3 left ear, 4 right ear
# 5 left shoulder, 6 right shoulder
# 7 left elbow, 8 right elbow
# 9 left wrist, 10 right wrist
# 11 left hip, 12 right hip
# 13 left knee, 14 right knee
# 15 left ankle, 16 right ankle
SKELETON = [
    (0, 1), (0, 2), (1, 3), (2, 4),
    (5, 6),
    (5, 7), (7, 9),
    (6, 8), (8, 10),
    (5, 11), (6, 12),
    (11, 12),
    (11, 13), (13, 15),
    (12, 14), (14, 16)
]

# Confidance
KP_CONF_THRES = 0.5
CONF_TH = 0.4

# Smoother
SMOOTHER_ALPHA = 0.4

# Dead zone
DEAD_ZONE = 10

# Max step limits
"""
1 = very smooth but slower
2 = good starting point
4 = faster but less smooth
"""
MAX_STEP_PAN = 2
MAX_STEP_TILT = 2


