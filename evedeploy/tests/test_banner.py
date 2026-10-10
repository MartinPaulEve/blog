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


class TestStackedWords:
    REMOTE = ("REMOTE", "BUILD", "SERVER")

    def test_default_wordmark_is_still_eve_gd(self):
        assert render_banner(color=False).splitlines()[4] == \
            "██████   ██   ██████ ██  ████  █████ "

    def test_words_stack_as_five_row_blocks_with_a_gap_between(self):
        art = render_banner(color=False, words=self.REMOTE).splitlines()
        # three words × 5 rows, two blank separators, then the blank + footer
        assert art[5] == "" and art[11] == ""
        assert all("██" in row for row in art[0:5] + art[6:11] + art[12:17])
        assert art[17] == "" and "evedeploy" in art[18]

    def test_each_word_spells_itself(self):
        art = render_banner(color=False, words=self.REMOTE).splitlines()
        # Bottom rows: R E M O T E / B U I L D / S E R V E R
        assert art[4] == "██  ██ ██████ ██  ██  ████    ██   ██████"
        assert art[10] == "█████   ████  ██████ ██████ █████ "
        assert art[16] == "█████  ██████ ██  ██   ██   ██████ ██  ██"

    def test_every_word_gets_the_full_gradient(self):
        art = render_banner(color=True, words=self.REMOTE).splitlines()
        for start in (0, 6, 12):
            for row, (r, g, b) in zip(art[start:start + 5], SNAFFLE_GRADIENT):
                assert row.startswith(f"\x1b[38;2;{r};{g};{b}m")

    def test_print_banner_takes_the_words(self):
        stream = io.StringIO()
        print_banner(stream=stream, color=False, words=("BUILD",))
        assert stream.getvalue().splitlines()[4] == "█████   ████  ██████ ██████ █████ "
