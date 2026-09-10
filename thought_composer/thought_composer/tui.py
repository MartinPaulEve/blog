"""The interactive composer: a prompt with a live Bluesky-limit count.

Enter posts, Alt+Enter inserts a newline, Ctrl+P pastes an image from
the clipboard, Ctrl+C (or Ctrl+D on an empty prompt) cancels. The
bottom toolbar shows the grapheme count against the 300 limit, how the
thought will post (one post or a thread), and the attachments.
"""

from prompt_toolkit import PromptSession
from prompt_toolkit.application import get_app
from prompt_toolkit.key_binding import KeyBindings

from . import clipboard
from .text import status_line


def compose(images: list[dict]) -> str | None:
    """Run the composer; return the text, or None when cancelled.

    ``images`` is a mutable list of ``{"data", "mime", "alt"}`` dicts:
    entries attached via --image are shown, and Ctrl+P appends pasted
    clipboard images to it live.
    """
    bindings = KeyBindings()

    @bindings.add("enter")
    def _submit(event):
        event.current_buffer.validate_and_handle()

    @bindings.add("escape", "enter")
    def _newline(event):
        event.current_buffer.insert_text("\n")

    @bindings.add("c-p")
    def _paste_image(event):
        pasted = clipboard.paste_image()
        if pasted:
            data, mime = pasted
            images.append({"data": data, "mime": mime, "alt": ""})

    def toolbar():
        text = get_app().current_buffer.text
        return (
            f" {status_line(text, images=len(images))}"
            "  —  Enter posts · Alt+Enter newline · Ctrl+P paste image"
        )

    session = PromptSession(
        multiline=True,
        key_bindings=bindings,
        bottom_toolbar=toolbar,
        prompt_continuation="  ",
    )
    try:
        return session.prompt("thought> ")
    except (KeyboardInterrupt, EOFError):
        return None


def ask_alt_text(images: list[dict]) -> None:
    """Prompt for alt text on any attachment that still lacks it."""
    for number, image in enumerate(images, 1):
        if not image.get("alt"):
            try:
                image["alt"] = input(
                    f"Alt text for image {number} (Enter to skip): "
                ).strip()
            except (KeyboardInterrupt, EOFError):
                return
