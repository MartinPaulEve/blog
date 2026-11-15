"""Drive the composer through a pipe: keystrokes in, returned text out."""

from unittest.mock import patch

from prompt_toolkit.application import create_app_session
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput

from thought_composer import tui

CTRL_V = "\x16"
CTRL_P = "\x10"
ENTER = "\r"


def run_composer(keys: str, images=None):
    with create_pipe_input() as pipe:
        pipe.send_text(keys)
        with create_app_session(input=pipe, output=DummyOutput()):
            return tui.compose(images if images is not None else [])


def test_typed_text_is_returned_on_enter():
    assert run_composer("hello" + ENTER) == "hello"


def test_ctrl_v_inserts_the_clipboard_text():
    with patch.object(tui.clipboard, "paste_text", lambda: "pasted words"), \
         patch.object(tui.clipboard, "paste_image", lambda: None):
        assert run_composer(CTRL_V + ENTER) == "pasted words"


def test_ctrl_v_inserts_at_the_cursor_between_typed_text():
    with patch.object(tui.clipboard, "paste_text", lambda: "MIDDLE"), \
         patch.object(tui.clipboard, "paste_image", lambda: None):
        assert run_composer("a " + CTRL_V + " z" + ENTER) == "a MIDDLE z"


def test_ctrl_v_pastes_multiline_text_without_submitting():
    with patch.object(tui.clipboard, "paste_text", lambda: "one\ntwo"), \
         patch.object(tui.clipboard, "paste_image", lambda: None):
        assert run_composer(CTRL_V + "!" + ENTER) == "one\ntwo!"


def test_ctrl_v_attaches_an_image_when_the_clipboard_holds_no_text():
    images = []
    with patch.object(tui.clipboard, "paste_text", lambda: None), \
         patch.object(tui.clipboard, "paste_image", lambda: (b"png", "image/png")):
        text = run_composer("look" + CTRL_V + ENTER, images)
    assert text == "look"
    assert images == [{"data": b"png", "mime": "image/png", "alt": ""}]


def test_ctrl_v_with_an_empty_clipboard_changes_nothing():
    images = []
    with patch.object(tui.clipboard, "paste_text", lambda: None), \
         patch.object(tui.clipboard, "paste_image", lambda: None):
        assert run_composer("same" + CTRL_V + ENTER, images) == "same"
    assert images == []


def test_ctrl_p_still_attaches_an_image():
    images = []
    with patch.object(tui.clipboard, "paste_image", lambda: (b"png", "image/png")):
        run_composer(CTRL_P + "x" + ENTER, images)
    assert images == [{"data": b"png", "mime": "image/png", "alt": ""}]
