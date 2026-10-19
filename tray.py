
from pystray import MenuItem as item
import pystray
from PIL import Image, ImageDraw

def create_image():
    # Create a simple icon image
    width = 64
    height = 64
    color1 = (0, 0, 0, 0)  # Transparent
    color2 = 'white'

    image = Image.new('RGBA', (width, height), color1)
    dc = ImageDraw.Draw(image)
    
    # Simple ghost shape
    dc.ellipse([(10, 20), (54, 60)], fill=color2)
    dc.ellipse([(20, 10), (44, 30)], fill=color2)
    dc.rectangle([(20, 20), (44, 60)], fill=color2)
    dc.ellipse([(25, 35), (30, 40)], fill='black') # Eye 1
    dc.ellipse([(34, 35), (39, 40)], fill='black') # Eye 2

    return image

def create_tray_icon(app):
    image = create_image()
    menu = (
        item('Show Window', app.show_window, default=True),
        item('Stop Mover', app.stop_mover),
        pystray.Menu.SEPARATOR,
        item('Exit', app.exit_app)
    )
    icon = pystray.Icon("ghost_mouse", image, "Ghost Mouse 👻", menu)
    return icon

