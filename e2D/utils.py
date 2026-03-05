from __future__ import annotations
from struct import pack
from typing import TYPE_CHECKING, Sequence
import os
import sys
import subprocess
import numpy as np
import moderngl

if TYPE_CHECKING:
    from ._types import ComputeShaderType, Number, ProgramAttrType, ProgramType, UniformBlockType, UniformType, pArray


def _is_array_uniform(u: UniformType) -> bool:
    return u.array_length > 1

def get_pattr(prog_id: str | ProgramType, name: str, *, programs: dict[str, ProgramType] = {}) -> ProgramAttrType:
    if isinstance(prog_id, moderngl.Program):
        return prog_id[name]
    if prog_id not in programs:
        raise ValueError(f"Program with id '{prog_id}' does not exist.")
    return programs[prog_id][name]

def get_uniform(prog_id: str | ProgramType | ComputeShaderType, name: str, *, compute_shaders: dict[str, ComputeShaderType] = {}, programs: dict[str, ProgramType] = {}) -> UniformType:
    if isinstance(prog_id, str):
        if prog_id in programs:
            prog_id = programs[prog_id]
        elif prog_id in compute_shaders:
            prog_id = compute_shaders[prog_id]
        else:
            raise ValueError(f"Program or compute shader with id '{prog_id}' does not exist.")

    attr = prog_id[name]
    if not isinstance(attr, moderngl.Uniform):
        raise TypeError(f"'{name}' is {type(attr).__name__}, not a Uniform")
    return attr

def get_uniform_block(prog_id: str | ProgramType, name: str, *, programs: dict[str, ProgramType] = {}) -> UniformBlockType:
    if isinstance(prog_id, str):
        if prog_id not in programs:
            raise ValueError(f"Program with id '{prog_id}' does not exist.")
        prog_id = programs[prog_id]

    attr = prog_id[name]
    if not isinstance(attr, moderngl.UniformBlock):
        raise TypeError(f"'{name}' is {type(attr).__name__}, not a UniformBlock")
    return attr

def set_uniform_block_binding(prog_id: str | ProgramType, name: str, binding: int, *, programs: dict[str, ProgramType] = {}) -> None:
    block = get_uniform_block(prog_id, name, programs=programs)
    block.binding = binding

def get_pattr_value(prog_id: str | ProgramType, name: str, *, programs: dict[str, ProgramType] = {}) -> Number | pArray:
    attr = get_pattr(prog_id, name, programs=programs)
    if not isinstance(attr, moderngl.Uniform):
        raise TypeError(f"'{name}' is {type(attr).__name__}, not a Uniform")
    if _is_array_uniform(attr):
        raise TypeError(f"Uniform '{name}' is an array; cannot use .value")
    return attr.value

def set_pattr_value(prog_id: str | ProgramType, name: str, value: Number | pArray, *, programs: dict[str, ProgramType] = {}, force_write: bool = False) -> None:
    attr = get_pattr(prog_id, name, programs=programs)
    if not isinstance(attr, moderngl.Uniform):
        raise TypeError(f"'{name}' is {type(attr).__name__}, not a Uniform")

    use_write = force_write or _is_array_uniform(attr)
    if use_write:
        data = value if isinstance(value, np.ndarray) else np.array(value, dtype="f4")
        attr.write(data.tobytes())
    else:
        attr.value = value

def set_pattr_value_packed(prog_id: str | ProgramType, name: str, format: str, value: Sequence[float]) -> None:
    attr = get_pattr(prog_id, name, programs={})
    if not isinstance(attr, moderngl.Uniform):
        raise TypeError(f"'{name}' is {type(attr).__name__}, not a Uniform")
    attr.write(pack(format, *value))

PI = np.pi
PI_HALF = np.pi / 2
PI_QUARTER = np.pi / 4
TAU = np.pi * 2


def find_system_font(font_name: str) -> str:
    """Resolve a font name/filename to an absolute path on the current OS.

    On Windows (and macOS) PIL/Pillow can find fonts by filename from the
    system font directories automatically, so the name is returned as-is.

    On Linux the Windows-style filenames (arial.ttf, consola.ttf …) are not
    present.  This function tries the following in order:
    1. Return the name unchanged if it is already an absolute path that exists.
    2. Use ``fc-match`` (fontconfig, available on all major distros) to find
       the best matching font file for the given family name.
    3. Walk the common Linux font directories looking for an exact filename match.
    4. Return the original name and let the caller handle the failure.
    """
    if sys.platform != "linux":
        return font_name

    # If it already looks like an absolute path that exists, use it directly.
    if os.path.isabs(font_name) and os.path.isfile(font_name):
        return font_name

    # Strip extension to get the family name that fc-match understands.
    base = font_name.rsplit(".", 1)[0] if "." in font_name else font_name

    try:
        result = subprocess.run(
            ["fc-match", "--format=%{file}", base],
            capture_output=True, text=True, timeout=3
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Fallback: search common font directories for an exact filename match.
    font_dirs = [
        "/usr/share/fonts",
        "/usr/local/share/fonts",
        os.path.expanduser("~/.fonts"),
        os.path.expanduser("~/.local/share/fonts"),
    ]
    font_lower = font_name.lower()
    for font_dir in font_dirs:
        if not os.path.isdir(font_dir):
            continue
        for root, _, files in os.walk(font_dir):
            for f in files:
                if f.lower() == font_lower:
                    return os.path.join(root, f)

    return font_name
