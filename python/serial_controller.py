import serial
import threading
import time


class SerialController:
    """
    Threaded serial controller for servo pan/tilt commands.
    Decouples the vision loop (30fps) from serial writes,
    always sending the latest position at a fixed interval.
    """

    def __init__(self, port, baud=115200, interval=0.05):
        """
        port     : serial port string, e.g. '/dev/cu.usbmodem1201'
        baud     : baud rate (default 115200)
        interval : seconds between serial writes (default 0.05 → 20Hz)
        """
        self.ser = serial.Serial(port, baud)
        time.sleep(2)  # wait for Arduino reset

        self.interval = interval
        self._lock = threading.Lock()
        self._pan = None
        self._tilt = None
        self._laser = None
        self._last_sent = (None, None, None)
        self._running = False
        self._thread = None

    def start(self):
        """Start the background serial writer thread."""
        self._running = True
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the background thread and close the serial port."""
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=1)
        if self.ser.is_open:
            self.ser.close()

    def update(self, pan, tilt, laser):
        """
        Called from the main/vision loop to set the latest target angles.
        Thread-safe — never blocks the caller.
        """
        with self._lock:
            self._pan = pan
            self._tilt = tilt
            self._laser = laser

    def _worker(self):
        """Background thread: sends latest (pan, tilt) at fixed interval,
        only when the value has actually changed."""
        while self._running:
            with self._lock:
                pan = self._pan
                tilt = self._tilt
                laser = self._laser

            if (pan, tilt, laser) != self._last_sent and pan is not None:
                command = f'{pan},{tilt},{laser}\n'
                self.ser.write(command.encode())
                self._last_sent = (pan, tilt, laser)

            time.sleep(self.interval)