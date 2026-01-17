import pystray
from pystray import MenuItem as item
from PIL import Image

def start_tray(controller):
    icon = Image.new("RGB", (64, 64), "black")

    menu = (
        item("Enable Gesture Mouse", controller.enable),
        item("Disable Gesture Mouse", controller.disable),
        item("Exit", lambda icon, item: icon.stop())
    )

    tray = pystray.Icon(
        "GestureMouse",
        icon,
        "Gesture Mouse Controller",
        menu
    )

    tray.run()
