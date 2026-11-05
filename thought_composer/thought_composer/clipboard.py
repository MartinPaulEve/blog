"""Reading text or an image off the system clipboard (Wayland first, then X11)."""

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


def paste_text() -> str | None:
    """The clipboard's text, or None when it holds none.

    Terminals keep Ctrl+V for themselves only as Ctrl+Shift+V; a bare
    Ctrl+V reaches the application as a control byte, so the composer
    binds it and pastes through this helper instead.
    """
    if shutil.which("wl-paste"):
        types = subprocess.run(
            ["wl-paste", "--list-types"], capture_output=True, text=True, check=False
        )
        if types.returncode == 0 and any(
            t.startswith("text/") or t in ("TEXT", "STRING", "UTF8_STRING")
            for t in types.stdout.split()
        ):
            grab = subprocess.run(
                ["wl-paste", "--no-newline"], capture_output=True, check=False
            )
            if grab.returncode == 0 and grab.stdout:
                return grab.stdout.decode("utf-8", errors="replace")
    if shutil.which("xclip"):
        grab = subprocess.run(
            ["xclip", "-selection", "clipboard", "-t", "UTF8_STRING", "-o"],
            capture_output=True,
            check=False,
        )
        if grab.returncode == 0 and grab.stdout:
            return grab.stdout.decode("utf-8", errors="replace")
    return None
