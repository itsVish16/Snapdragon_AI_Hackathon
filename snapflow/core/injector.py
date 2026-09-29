import sys
import subprocess
from typing import Optional


class TextInjector:
    def __init__(self, use_clipboard_fallback: bool = True):
        self.use_clipboard_fallback = use_clipboard_fallback

    def copy_to_clipboard(self, text: str) -> bool:
        if not text:
            return False

        try:
            if sys.platform == "darwin":
                p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE, close_fds=True)
                p.communicate(input=text.encode("utf-8"))
                return True
            elif sys.platform.startswith("win"):
                p = subprocess.Popen(["clip"], stdin=subprocess.PIPE, close_fds=True)
                p.communicate(input=text.encode("utf-16"))
                return True
            else:
                p = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE, close_fds=True)
                p.communicate(input=text.encode("utf-8"))
                return True
        except Exception:
            return False

    def type_text(self, text: str) -> bool:
        if not text:
            return False

        copied = self.copy_to_clipboard(text)

        try:
            if sys.platform == "darwin":
                applescript = """
                tell application "System Events"
                    keystroke "v" using command down
                end tell
                """
                subprocess.run(["osascript", "-e", applescript], check=True, capture_output=True)
                return True
            elif sys.platform.startswith("win"):
                ps_script = """
                Add-Type -AssemblyName System.Windows.Forms
                [System.Windows.Forms.SendKeys]::SendWait('^v')
                """
                subprocess.run(["powershell", "-Command", ps_script], check=True, capture_output=True)
                return True
        except Exception:
            pass

        return copied
