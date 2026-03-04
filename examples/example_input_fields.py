"""
example_input_fields.py — Phase 3 input widgets demo  (updated for Phase 4 containers).

Demonstrates every Phase 3 text-entry widget inside Phase 4 VBox containers:
  - InputField       (plain, password, validated)
  - MultiLineInput   (fixed-height + scrollbar  &  auto-expand)

Left panel:   input widgets inside a VBox container
Right panel:  live “Submitted Values” display + clipboard cheatsheet (VBox)

Controls:
  Tab / Shift+Tab  — cycle input focus between fields
  Enter            — submit the focused InputField
  Ctrl+Enter       — submit the focused MultiLineInput
  Ctrl+C / X / V   — copy / cut / paste (via GLFW clipboard)
  Ctrl+A           — select all text in the focused field
  T                — cycle theme
  F3               — toggle debug outlines
  ESC              — quit
"""

import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
import glfw

from e2D import (
    RootEnv, DefEnv, V2, WindowConfig,
    Keys, KeyState, TextStyle,
    WHITE, GREEN, YELLOW, CYAN,
)
from e2D.colors import Color
from e2D.ui import VBox, SizeMode
from e2D.ui.theme import (
    MONOKAI_THEME, DARK_THEME, LIGHT_THEME,
    SOLARIZED_DARK, SOLARIZED_LIGHT,
    NORD_THEME, DRACULA_THEME,
    TOKYO_NIGHT_THEME, HIGH_CONTRAST,
)

_THEMES = [
    ("Monokai",        MONOKAI_THEME),
    ("Dark",           DARK_THEME),
    ("Light",          LIGHT_THEME),
    ("Solarized Dark", SOLARIZED_DARK),
    ("Solarized Light",SOLARIZED_LIGHT),
    ("Nord",           NORD_THEME),
    ("Dracula",        DRACULA_THEME),
    ("Tokyo Night",    TOKYO_NIGHT_THEME),
    ("High Contrast",  HIGH_CONTRAST),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def sty(size: int, color=None) -> TextStyle:
    c = color if color is not None else WHITE
    return TextStyle(font_size=size, color=c)

# Keep legacy alias for callbacks
style = sty

WIN_W  = 900
WIN_H  = 730
SEP_X  = 460      # x-coordinate of the vertical separator line
F_W    = 430      # width of every InputField / MultiLineInput

_LGRAY = Color(0.45, 0.45, 0.45)   # light grey — section-hint text
_DGRAY = Color(0.30, 0.30, 0.30)   # darker grey — small annotation text


# ---------------------------------------------------------------------------
# Example class
# ---------------------------------------------------------------------------

class InputFieldsExample(DefEnv):
    """Phase 3 demo: InputField and MultiLineInput widgets."""

    def __init__(self, root: RootEnv) -> None:
        self.root  = root
        self._theme_idx = 0
        root.ui.theme = _THEMES[0][1]

        ui = root.ui

        # ── Left panel VBox ──────────────────────────────────────────────────
        left = ui.vbox(
            spacing=4,
            position=V2(0, 0),
            size=V2(SEP_X, WIN_H),
            bg_color=Color(0.07, 0.07, 0.11, 1.0),
            border_color=Color(0.20, 0.20, 0.35, 1.0),
            border_width=1.0,
            padding=12,
        )

        def _add(widget):
            left.add_child(widget)
            return widget

        def _sec(text: str):
            lb = ui.label("", default_style=sty(10, _DGRAY))
            lb.set_plain_text(text)
            left.add_child(lb)

        def _lbl(text: str, color=None):
            lb = ui.label("", default_style=sty(14, color or WHITE))
            lb.set_plain_text(text)
            left.add_child(lb)
            return lb

        # Title + hints
        _add(ui.label("Phase 3 — Input Fields", default_style=sty(22, WHITE)))
        _add(ui.label(
            "Tab = next field   |   T = theme   |   F3 = debug   |   ESC = quit",
            default_style=sty(11, _LGRAY),
        ))

        # ── Section 1: plain InputField ──────────────────────────────────────
        _sec("INPUTFIELD — plain text  (Enter to submit)")
        _lbl("Name:")
        self._field_name = _add(ui.input_field(
            placeholder="Enter your name…",
            on_submit=self._on_name,
            size=V2(F_W, 32),
            tab_index=0,
        ))

        # ── Section 2: password InputField ──────────────────────────────────
        _sec("INPUTFIELD — password  (Enter to submit)")
        _lbl("Password:")
        self._field_password = _add(ui.input_field(
            placeholder="Enter password…",
            password=True,
            on_submit=self._on_password,
            size=V2(F_W, 32),
            tab_index=1,
        ))

        # ── Section 3: validated InputField (port 1–65535) ──────────────────
        _sec("INPUTFIELD — validated  (port 1–65535, red border = invalid)")
        _lbl("Port:")
        self._field_port = _add(ui.input_field(
            placeholder="8080",
            validate=self._validate_port,
            on_submit=self._on_port,
            size=V2(F_W, 32),
            tab_index=2,
        ))
        _add(ui.label(
            "↑  border turns red when value is not a valid port number",
            default_style=sty(11, _DGRAY),
        ))

        # ── Section 4: MultiLineInput — scrollable ───────────────────────────
        _sec("MULTILINE — scrollable  (Ctrl+Enter = submit,  Tab = indent)")
        _lbl("Notes:")
        self._field_notes = _add(ui.multi_line_input(
            placeholder=(
                "Type here…\n"
                "Press Enter for a new line.\n"
                "Scroll with the mouse wheel.\n"
                "Ctrl+Enter to submit."
            ),
            on_submit=self._on_notes,
            auto_expand=False,
            show_scrollbar=True,
            size=V2(F_W, 100),
            tab_index=3,
        ))

        # ── Section 5: MultiLineInput — auto-expand ──────────────────────────
        _sec("MULTILINE — auto-expand  (min 44px, max 160px, Ctrl+Enter = submit)")
        _lbl("Description:")
        self._field_desc = _add(ui.multi_line_input(
            placeholder=(
                "This field grows to fit content.\n"
                "Min height = 44 px, max height = 160 px.\n"
                "Beyond the max it scrolls."
            ),
            show_scrollbar=True,
            auto_expand=True,
            min_height=44.0,
            max_height=160.0,
            size=V2(F_W, 44),
            tab_index=4,
        ))

        # ── Right panel VBox ─────────────────────────────────────────────────
        right = ui.vbox(
            spacing=6,
            position=V2(SEP_X, 0),
            size=V2(WIN_W - SEP_X, WIN_H),
            bg_color=Color(0.05, 0.05, 0.09, 1.0),
            border_color=Color(0.20, 0.20, 0.35, 1.0),
            border_width=1.0,
            padding=14,
        )

        def _radd(widget):
            right.add_child(widget)
            return widget

        _radd(ui.label("Submitted Values", default_style=sty(18, CYAN)))

        self._lbl_name = _radd(ui.label(
            ("Name:     ", sty(13, _LGRAY)),
            ("—", sty(13, YELLOW)),
            default_style=sty(13, WHITE),
        ))
        self._lbl_password = _radd(ui.label(
            ("Password: ", sty(13, _LGRAY)),
            ("—", sty(13, YELLOW)),
            default_style=sty(13, WHITE),
        ))
        self._lbl_port = _radd(ui.label(
            ("Port:     ", sty(13, _LGRAY)),
            ("—", sty(13, YELLOW)),
            default_style=sty(13, WHITE),
        ))
        self._lbl_notes = _radd(ui.label(
            ("Notes:    ", sty(13, _LGRAY)),
            ("—", sty(13, YELLOW)),
            default_style=sty(13, WHITE),
        ))

        _radd(ui.label("Current field value (live):", default_style=sty(12, _LGRAY)))
        self._lbl_live = _radd(ui.label("", default_style=sty(13, WHITE)))

        _radd(ui.label("Shortcuts:", default_style=sty(13, _LGRAY)))
        hints = [
            "  Ctrl+C   — copy selection",
            "  Ctrl+X   — cut selection",
            "  Ctrl+V   — paste from clipboard",
            "  Ctrl+A   — select all",
            "  Ctrl+Z   — undo last char",
            "  Home/End — jump to line start/end",
            "  Shift+←/→ — extend selection",
        ]
        for hint in hints:
            lb = ui.label("", default_style=sty(12, _LGRAY))
            lb.set_plain_text(hint)
            right.add_child(lb)


    # -----------------------------------------------------------------------
    # Validation
    # -----------------------------------------------------------------------

    @staticmethod
    def _validate_port(text: str) -> bool:
        try:
            return 1 <= int(text) <= 65535
        except ValueError:
            return False

    # -----------------------------------------------------------------------
    # Submit callbacks
    # -----------------------------------------------------------------------

    def _on_name(self, value: str) -> None:
        self._lbl_name.set_text(
            ("Name:     ", style(13, _LGRAY)),
            (value or "—", style(13, GREEN if value else YELLOW)),
        )

    def _on_password(self, value: str) -> None:
        masked = "*" * len(value) if value else "—"
        self._lbl_password.set_text(
            ("Password: ", style(13, _LGRAY)),
            (masked, style(13, GREEN if value else YELLOW)),
        )

    def _on_port(self, value: str) -> None:
        self._lbl_port.set_text(
            ("Port:     ", style(13, _LGRAY)),
            (value or "—", style(13, GREEN if value else YELLOW)),
        )

    def _on_notes(self, value: str) -> None:
        n = (value.count("\n") + 1) if value else 0
        self._lbl_notes.set_text(
            ("Notes:    ", style(13, _LGRAY)),
            (f"{n} line(s)" if value else "—", style(13, GREEN if value else YELLOW)),
        )

    # -----------------------------------------------------------------------
    # Lifecycle
    # -----------------------------------------------------------------------

    def update(self) -> None:
        kb = self.root.keyboard

        # T — cycle through all themes
        if kb.get_key(Keys.T, KeyState.JUST_PRESSED):
            self._theme_idx = (self._theme_idx + 1) % len(_THEMES)
            name, theme = _THEMES[self._theme_idx]
            self.root.ui.theme = theme

        # ESC — quit
        if kb.get_key(Keys.ESCAPE, KeyState.JUST_PRESSED):
            glfw.set_window_should_close(self.root.window, True)

        # Live preview: display the focused field's current text
        fields = (
            self._field_name,
            self._field_password,
            self._field_port,
            self._field_notes,
            self._field_desc,
        )
        for field in fields:
            if field.focused:
                raw = field.value
                if field is self._field_password:
                    raw = "*" * len(raw)   # mask password characters
                if len(raw) > 55:
                    raw = raw[:55] + "…"
                self._lbl_live.set_plain_text(raw)
                break
        else:
            self._lbl_live.set_plain_text("")

    def draw(self) -> None:
        # VBox containers cover the full window with their own bg_color.
        pass


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    config = WindowConfig(
        size=V2(WIN_W, WIN_H),
        title="e2D Phase 3 — Input Fields (Phase 4 layout)",
        target_fps=60,
        vsync=False,
    )
    root = RootEnv(config=config)
    root.init(env := InputFieldsExample(root))
    root.loop()


if __name__ == "__main__":
    main()
