"""Reading an image off the system clipboard (Wayland first, then X11)."""

import shutil
import subprocess


def paste_image() -> tuple[bytes, str] | None:
    """(bytes, mime) from the clipboard, or None when it holds no image."""
    if shutil.which("wl-paste"):
        types = subprocess.run(
            ["wl-paste", "--list-types"], capture_output=True, text=True, check=False
        )
        if types.returncode == 0:
            mimes = [t for t in types.stdout.split() if t.startswith("image/")]
            if mimes:
                mime = "image/png" if "image/png" in mimes else mimes[0]
                grab = subprocess.run(
                    ["wl-paste", "--type", mime], capture_output=True, check=False
                )
                if grab.returncode == 0 and grab.stdout:
                    return grab.stdout, mime
    if shutil.which("xclip"):
        for mime in ("image/png", "image/jpeg"):
            grab = subprocess.run(
                ["xclip", "-selection", "clipboard", "-t", mime, "-o"],
                capture_output=True,
                check=False,
            )
            if grab.returncode == 0 and grab.stdout:
                return grab.stdout, mime
    return None
