import io
import re

from evedeploy import __version__
from evedeploy.banner import print_banner, render_banner

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

# The exact gradient stops used by the snaffle wordmark, top to bottom.
SNAFFLE_GRADIENT = [
    (34, 211, 238),
    (38, 211, 217),
    (43, 211, 196),
    (47, 211, 174),
    (52, 211, 153),
]


class TestRenderBanner:
    def test_plain_render_has_no_ansi_codes(self):
        assert not ANSI_RE.search(render_banner(color=False))

    def test_wordmark_is_five_rows_of_block_art(self):
        rows = render_banner(color=False).splitlines()[:5]
        assert len(rows) == 5
        assert all("██" in row for row in rows)

    def test_wordmark_spells_eve_gd(self):
        # The bottom row is the only one where every glyph, including the
        # dot, paints cells: E, V (narrowed to its point), E, dot, G, D
        # joined by single spaces.
        bottom = render_banner(color=False).splitlines()[4]
        assert bottom == "██████   ██   ██████ ██  ████  █████ "

    def test_colored_rows_use_the_snaffle_gradient(self):
        rows = render_banner(color=True).splitlines()[:5]
        for row, (r, g, b) in zip(rows, SNAFFLE_GRADIENT):
            assert row.startswith(f"\x1b[38;2;{r};{g};{b}m")
            assert row.endswith("\x1b[0m")

    def test_footer_carries_name_tagline_and_version(self):
        footer = render_banner(color=False).splitlines()[-1]
        assert "evedeploy" in footer
        assert f"v{__version__}" in footer


class TestPrintBanner:
    def test_writes_to_given_stream(self):
        stream = io.StringIO()
        print_banner(stream=stream, color=False)
        assert "██" in stream.getvalue()

    def test_no_color_env_disables_color(self, monkeypatch):
        monkeypatch.setenv("NO_COLOR", "1")
        stream = io.StringIO()
        print_banner(stream=stream)
        assert not ANSI_RE.search(stream.getvalue())

    def test_force_color_env_enables_color_on_non_tty(self, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        monkeypatch.setenv("FORCE_COLOR", "1")
        stream = io.StringIO()
        print_banner(stream=stream)
        assert ANSI_RE.search(stream.getvalue())

    def test_non_tty_defaults_to_plain(self, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        monkeypatch.delenv("FORCE_COLOR", raising=False)
        stream = io.StringIO()
        print_banner(stream=stream)
        assert not ANSI_RE.search(stream.getvalue())
