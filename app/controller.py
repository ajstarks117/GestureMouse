# Controls enable/disable logic
import threading
from app.gesture.hand_tracker import start_gesture_mouse

class GestureController:
    def __init__(self):
        self.active = False
        self.thread = None

    def enable(self, icon=None, item=None):
        if not self.active:
            self.active = True
            self.thread = threading.Thread(
                target=start_gesture_mouse,
                args=(self,)
            )
            self.thread.daemon = True
            self.thread.start()

    def disable(self, icon=None, item=None):
        self.active = False
