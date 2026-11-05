import subprocess
from unittest.mock import patch

from thought_composer import clipboard


def fake_run(responses):
    """A subprocess.run stand-in answering from {argv-tuple: (code, stdout)}."""

    def run(argv, **kwargs):
        code, out = responses.get(tuple(argv), (1, b""))
        if kwargs.get("text"):
            out = out.decode() if isinstance(out, bytes) else out
        return subprocess.CompletedProcess(argv, code, stdout=out, stderr="")

    return run


def test_paste_text_reads_wayland_clipboard():
    responses = {
        ("wl-paste", "--list-types"): (0, "text/plain;charset=utf-8\nTEXT\n"),
        ("wl-paste", "--no-newline"): (0, b"hello from wayland"),
    }
    with patch.object(clipboard.shutil, "which", lambda name: name == "wl-paste"), \
         patch.object(clipboard.subprocess, "run", fake_run(responses)):
        assert clipboard.paste_text() == "hello from wayland"


def test_paste_text_keeps_internal_newlines():
    responses = {
        ("wl-paste", "--list-types"): (0, "text/plain\n"),
        ("wl-paste", "--no-newline"): (0, b"line one\nline two"),
    }
    with patch.object(clipboard.shutil, "which", lambda name: name == "wl-paste"), \
         patch.object(clipboard.subprocess, "run", fake_run(responses)):
        assert clipboard.paste_text() == "line one\nline two"


def test_paste_text_returns_none_when_wayland_clipboard_holds_only_an_image():
    responses = {
        ("wl-paste", "--list-types"): (0, "image/png\n"),
        ("wl-paste", "--no-newline"): (0, b"\x89PNG..."),
    }
    with patch.object(clipboard.shutil, "which", lambda name: name == "wl-paste"), \
         patch.object(clipboard.subprocess, "run", fake_run(responses)):
        assert clipboard.paste_text() is None


def test_paste_text_falls_back_to_xclip():
    responses = {
        ("xclip", "-selection", "clipboard", "-t", "UTF8_STRING", "-o"): (
            0,
            b"hello from x11",
        ),
    }
    with patch.object(clipboard.shutil, "which", lambda name: name == "xclip"), \
         patch.object(clipboard.subprocess, "run", fake_run(responses)):
        assert clipboard.paste_text() == "hello from x11"


def test_paste_text_returns_none_without_any_clipboard_tool():
    with patch.object(clipboard.shutil, "which", lambda name: None):
        assert clipboard.paste_text() is None


def test_paste_text_returns_none_for_an_empty_clipboard():
    responses = {
        ("wl-paste", "--list-types"): (0, "text/plain\n"),
        ("wl-paste", "--no-newline"): (0, b""),
    }
    with patch.object(clipboard.shutil, "which", lambda name: name == "wl-paste"), \
         patch.object(clipboard.subprocess, "run", fake_run(responses)):
        assert clipboard.paste_text() is None
