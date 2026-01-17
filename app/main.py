# Entry point (starts app)
from app.controller import GestureController
from app.ui.tray_app import start_tray

def start_app():
    controller = GestureController()
    start_tray(controller)
