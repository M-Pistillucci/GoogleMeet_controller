import time
from GoogleMeetController import GoogleMeetController

controller = GoogleMeetController(host="127.0.0.1", port=8765)
controller.start()

print("Server WebSocket avviato, in ascolto su 127.0.0.1:8765. Ctrl+C per uscire.")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    controller.stop()
