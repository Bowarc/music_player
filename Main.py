# cd C:\DJ_Office\Students\Heto\Step_02
# python Mai275375n.py
import os
import win32con
import win32gui
from App.Uis.UI_Loader import Main_UI
from PyQt5.QtWidgets import QApplication

__Author__ = "Bowarc"
__Contact__ = "Discord: Bowarc"


def close_console():
    # input("Press enter to hide this console and start the app.")
    user_input = input("Do you want to close the console ?\n[USER]>")
    if user_input.lower().startswith("y") or user_input.lower().startswith("o"):
        the_program_to_hide = win32gui.GetForegroundWindow()
        win32gui.ShowWindow(the_program_to_hide, win32con.SW_HIDE)


with open("bug_report.txt", "w") as f:
    f.write("")

if __name__ == "__main__":
    # This creates the Main Event Handler for a PyQt Application
    MainEvntThread = QApplication([])

    try:
        close_console()
        MainApp = Main_UI()
        MainApp.show()

    except Exception as e:
        import traceback
        import sys
        print(traceback.format_exc())

        with open("bug_report.txt", "w") as f:
            f.write(traceback.format_exc())
        sys.exit()

    MainEvntThread.exec()
