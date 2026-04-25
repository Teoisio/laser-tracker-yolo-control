import numpy as np

class KeypointSmoother:

    def __init__(self, alpha=0.4, conf_th=0.5):
        self.alpha = alpha
        self.conf_th = conf_th
        self._prev = None

    def update(self, kps_xy, kps_conf):
        if self._prev is None:
            self._prev = kps_xy.copy()
            return self._prev

        smoothed = self._prev.copy()

        for j in range(len(kps_xy)):
            if kps_conf is None or kps_conf[j] > self.conf_th:
                smoothed[j] = self.alpha * kps_xy[j] + (1 - self.alpha) * self._prev[j]
            # if confidence too low → keep previous value unchanged

        self._prev = smoothed
        return smoothed
    def reset(self):
        self._prev = None