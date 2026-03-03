"""
example_input_fields.py — Phase 3 input widgets demo.

Demonstrates every Phase 3 text-entry widget:
  - InputField       (plain, password, validated)
  - MultiLineInput   (fixed-height + scrollbar  &  auto-expand)

Left panel:   all input widgets
Right panel:  live "Submitted Values" display + clipboard cheatsheet

Controls:
  Tab / Shift+Tab  — cycle input focus between fields
  Enter            — submit the focused InputField
  Ctrl+Enter       — submit the focused MultiLineInput
  Ctrl+C / X / V   — copy / cut / paste (via GLFW clipboard)
  Ctrl+A           — select all text in the focused field
  T                — toggle DARK / LIGHT theme
  ESC              — quit
"""

import glfw

from e2D import (
    RootEnv, DefEnv, V2, WindowConfig,
    Keys, KeyState, TextStyle,
    WHITE, GREEN, YELLOW, CYAN,
)
from e2D.colors import Color
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

def style(size: int, color=None) -> TextStyle:
    c = color if color is not None else WHITE
    return TextStyle(font_size=size, color=c)


SEP_X  = 470        # x-coordinate of the vertical separator line
F_X    = 20         # left margin for labels and fields
F_W    = 430        # width of every InputField / MultiLineInput

_LGRAY = Color(0.45, 0.45, 0.45)   # light grey — section-hint text
_DGRAY = Color(0.30, 0.30, 0.30)   # darker grey — small annotation text


# ---------------------------------------------------------------------------
# Example class
# ---------------------------------------------------------------------------

class InputFieldsExample(DefEnv):
    """Phase 3 demo: InputField and MultiLineInput widgets."""

    def __init__(self, root: RootEnv) -> None:
        self.root  = root
        self._theme_idx = 0   # start on Monokai
        root.ui.theme = _THEMES[0][1]

        ui = root.ui

        # -------------------------------------------------------------------
        # Title + key hints
        # -------------------------------------------------------------------
        ui.label(
            "Phase 3 — Input Fields",
            position=V2(F_X, 12),
            default_style=style(24, WHITE),
        )
        ui.label(
            "Tab = next field   |   T = next theme   |   ESC = quit",
            position=V2(F_X, 43),
            default_style=style(13, _LGRAY),
        )

        # -------------------------------------------------------------------
        # Section 1: plain InputField
        # -------------------------------------------------------------------
        ui.label(
            "INPUTFIELD — plain text  (Enter to submit)",
            position=V2(F_X, 72),
            default_style=style(11, _DGRAY),
        )
        ui.label("Name:", position=V2(F_X, 90), default_style=style(14, WHITE))
        self._field_name = ui.input_field(
            placeholder="Enter your name…",
            on_submit=self._on_name,
            position=V2(F_X, 110),
            size=V2(F_W, 32),
            tab_index=0,
        )

        # -------------------------------------------------------------------
        # Section 2: password InputField
        # -------------------------------------------------------------------
        ui.label(
            "INPUTFIELD — password  (Enter to submit)",
            position=V2(F_X, 158),
            default_style=style(11, _DGRAY),
        )
        ui.label("Password:", position=V2(F_X, 176), default_style=style(14, WHITE))
        self._field_password = ui.input_field(
            placeholder="Enter password…",
            password=True,
            on_submit=self._on_password,
            position=V2(F_X, 196),
            size=V2(F_W, 32),
            tab_index=1,
        )

        # -------------------------------------------------------------------
        # Section 3: validated InputField  (port number 1–65535)
        # -------------------------------------------------------------------
        ui.label(
            "INPUTFIELD — validated  (port 1–65535, red border = invalid)",
            position=V2(F_X, 244),
            default_style=style(11, _DGRAY),
        )
        ui.label("Port:", position=V2(F_X, 262), default_style=style(14, WHITE))
        self._field_port = ui.input_field(
            placeholder="8080",
            validate=self._validate_port,
            on_submit=self._on_port,
            position=V2(F_X, 282),
            size=V2(F_W, 32),
            tab_index=2,
        )
        ui.label(
            "↑  border turns red when the value is not a valid port number",
            position=V2(F_X, 322),
            default_style=style(11, _DGRAY),
        )

        # -------------------------------------------------------------------
        # Section 4: MultiLineInput — scrollable notes field
        # -------------------------------------------------------------------
        ui.label(
            "MULTILINE — scrollable  (Ctrl+Enter = submit,  Tab = indent)",
            position=V2(F_X, 347),
            default_style=style(11, _DGRAY),
        )
        ui.label("Notes:", position=V2(F_X, 365), default_style=style(14, WHITE))
        self._field_notes = ui.multi_line_input(
            placeholder=(
                "Type here…\n"
                "Press Enter for a new line.\n"
                "Scroll with the mouse wheel.\n"
                "Ctrl+Enter to submit."
            ),
            on_submit=self._on_notes,
            auto_expand=False,
            show_scrollbar=True,
            position=V2(F_X, 385),
            size=V2(F_W, 100),
            tab_index=3,
        )

        # -------------------------------------------------------------------
        # Section 5: MultiLineInput — auto-expand (grows to fit content)
        # -------------------------------------------------------------------
        ui.label(
            "MULTILINE — auto-expand  (min 44px, max 160px, Ctrl+Enter = submit)",
            position=V2(F_X, 502),
            default_style=style(11, _DGRAY),
        )
        ui.label("Description:", position=V2(F_X, 520), default_style=style(14, WHITE))
        self._field_desc = ui.multi_line_input(
            placeholder=(
                "This field grows to fit content.\n"
                "Min height = 44 px, max height = 160 px.\n"
                "Beyond the max it scrolls."
            ),
            show_scrollbar=True,
            auto_expand=True,
            min_height=44.0,
            max_height=160.0,
            position=V2(F_X, 540),
            size=V2(F_W, 44),
            tab_index=4,
        )

        # -------------------------------------------------------------------
        # Right panel — submitted values display
        # -------------------------------------------------------------------
        rp = SEP_X + 20     # right panel left margin

        ui.label(
            "Submitted Values",
            position=V2(rp, 12),
            default_style=style(18, CYAN),
        )

        self._lbl_name = ui.label(
            ("Name:     ", style(13, _LGRAY)),
            ("—", style(13, YELLOW)),
            position=V2(rp, 52),
            default_style=style(13, WHITE),
        )
        self._lbl_password = ui.label(
            ("Password: ", style(13, _LGRAY)),
            ("—", style(13, YELLOW)),
            position=V2(rp, 76),
            default_style=style(13, WHITE),
        )
        self._lbl_port = ui.label(
            ("Port:     ", style(13, _LGRAY)),
            ("—", style(13, YELLOW)),
            position=V2(rp, 100),
            default_style=style(13, WHITE),
        )
        self._lbl_notes = ui.label(
            ("Notes:    ", style(13, _LGRAY)),
            ("—", style(13, YELLOW)),
            position=V2(rp, 124),
            default_style=style(13, WHITE),
        )

        # Live preview of the currently-focused field's text
        ui.label(
            "Current field value (live):",
            position=V2(rp, 165),
            default_style=style(13, _LGRAY),
        )
        self._lbl_live = ui.label(
            "",
            position=V2(rp, 185),
            default_style=style(13, WHITE),
        )

        # Clipboard / shortcut cheatsheet
        ui.label(
            "Shortcuts:",
            position=V2(rp, 240),
            default_style=style(13, _LGRAY),
        )
        hints = [
            "  Ctrl+C   — copy selection",
            "  Ctrl+X   — cut selection",
            "  Ctrl+V   — paste from clipboard",
            "  Ctrl+A   — select all",
            "  Ctrl+Z   — undo last char",
            "  Home/End — jump to line start/end",
            "  Shift+←/→ — extend selection",
        ]
        for i, hint in enumerate(hints):
            ui.label(
                hint,
                position=V2(rp, 262 + i * 22),
                default_style=style(12, _LGRAY),
            )

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
        root = self.root
        w, h = root.window_size.x, root.window_size.y
        theme = root.ui.theme
        bg = theme.bg_window
        sep_c = theme.border_color

        # Left panel background (slightly lighter/darker than window bg)
        root.draw_rect(V2(0, 0), V2(SEP_X, h),
                       color=(bg.r + 0.01, bg.g + 0.01, bg.b + 0.01, 1.0))
        # Right panel background
        root.draw_rect(V2(SEP_X, 0), V2(w - SEP_X, h),
                       color=(max(0.0, bg.r - 0.01), max(0.0, bg.g - 0.01),
                              max(0.0, bg.b - 0.01), 1.0))
        # Separator line
        root.draw_line(V2(SEP_X, 0), V2(SEP_X, h),
                       color=(sep_c.r, sep_c.g, sep_c.b, sep_c.a), width=1.0)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    config = WindowConfig(
        size=V2(900, 730),
        title="e2D Phase 3 — Input Fields",
        target_fps=60,
        vsync=False,
    )
    root = RootEnv(config=config)
    root.init(env := InputFieldsExample(root))
    root.loop()


if __name__ == "__main__":
    main()
