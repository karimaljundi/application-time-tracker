from win32gui import GetWindowText, GetForegroundWindow
import time




time.sleep(3)
print(GetWindowText(GetForegroundWindow()))

