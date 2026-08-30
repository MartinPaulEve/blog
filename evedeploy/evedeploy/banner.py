"""Old-school block-pixel ``eve.gd`` banner with a cyan→green gradient.

Same wordmark treatment as the snaffle CLI: a solid block-pixel word painted
with a vertical truecolor gradient, sent to stderr so piped stdout stays
clean. Colour auto-disables when the target stream is not a TTY, when
``NO_COLOR`` is set, or can be forced on with ``FORCE_COLOR``.
"""

from __future__ import annotations

import os
import sys

from evedeploy import __version__

# ── Block-pixel font: 5 rows tall, 2-cell-wide strokes so each letter reads
# as one solid shape under the gradient. The dot is narrow on purpose. ──────
_GLYPHS = {
    "E": ["██████", "██    ", "█████ ", "██    ", "██████"],
    "V": ["██  ██", "██  ██", "██  ██", " ████ ", "  ██  "],
    ".": ["  ", "  ", "  ", "  ", "██"],
    "G": [" █████", "██    ", "██ ███", "██  ██", " ████ "],
    "D": ["█████ ", "██  ██", "██  ██", "██  ██", "█████ "],
}
_WORD = "EVE.GD"
_ROWS = 5

# Vertical gradient stops, cyan → aqua → green, one colour per wordmark row.
_GRADIENT = [
    (34, 211, 238),
    (38, 211, 217),
    (43, 211, 196),
    (47, 211, 174),
    (52, 211, 153),
]
_TAGLINE_RGB = (148, 163, 184)  # slate grey
_VERSION_RGB = (52, 211, 153)  # green, like the wordmark's foot

_TAGLINE = "build, publish and deploy the blog"
_RESET = "\x1b[0m"


def render_banner(color: bool = True) -> str:
    """Return the multi-line block-pixel banner as a string.

    When ``color`` is true each wordmark row is wrapped in a 24-bit ANSI
    colour from the cyan→green gradient; when false the plain block art is
    returned.
    """
    lines = []
    for row in range(_ROWS):
        cells = " ".join(_GLYPHS[ch][row] for ch in _WORD)
        lines.append(_rgb(_GRADIENT[row], cells, color))

    tagline = _rgb(_TAGLINE_RGB, f"evedeploy · {_TAGLINE}", color)
    version = _rgb(_VERSION_RGB, f"v{__version__}", color)
    footer = f"{tagline}   {version}"
    return "\n".join([*lines, "", footer]) + "\n"


def print_banner(stream=None, color: bool | None = None) -> None:
    """Paint the banner to the given stream (stderr by default).

    The stderr default is resolved at call time, not definition time, so
    stream redirection (tests, harnesses) is honoured.
    """
    if stream is None:
        stream = sys.stderr
    if color is None:
        color = _supports_color(stream)
    stream.write(render_banner(color=color))
    stream.flush()


def _rgb(rgb: tuple[int, int, int], text: str, on: bool) -> str:
    if not on:
        return text
    r, g, b = rgb
    return f"\x1b[38;2;{r};{g};{b}m{text}{_RESET}"


def _supports_color(stream) -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    force = os.environ.get("FORCE_COLOR")
    if force is not None:
        return force.strip().lower() not in ("0", "false", "no", "off", "")
    try:
        return bool(stream.isatty())
    except Exception:  # noqa: BLE001
        return False
