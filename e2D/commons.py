import numpy as np
from .types import ComputeShaderType, Number, ProgramAttrType, ProgramType, UniformBlockType, UniformType, pArray

def _is_array_uniform(u: UniformType) -> bool:
    return u.array_length > 1

def get_pattr(prog_id: str | ProgramType, name: str, *, programs: dict[str, ProgramType] = {}) -> ProgramAttrType:
    if isinstance(prog_id, ProgramType):
        return prog_id[name]
    if prog_id not in programs:
        raise ValueError(f"Program with id '{prog_id}' does not exist.")
    return programs[prog_id][name]
    
def get_uniform(prog_id: str | ProgramType | ComputeShaderType, name: str, *, compute_shaders: dict[str, ComputeShaderType] = {}, programs: dict[str, ProgramType] = {}) -> UniformType:
    """Get a uniform from a program or compute shader with proper typing.
    
    This is a type-safe alternative to program[name] which returns a union type.
    Raises TypeError if the attribute is not a Uniform.
    """
    if isinstance(prog_id, str):
        if prog_id in programs:
            prog_id = programs[prog_id]
        elif prog_id in compute_shaders:
            prog_id = compute_shaders[prog_id]
        else:
            raise ValueError(f"Program or compute shader with id '{prog_id}' does not exist.")
    
    attr = prog_id[name]
    if not isinstance(attr, UniformType):
        raise TypeError(f"'{name}' is {type(attr).__name__}, not a Uniform")
    return attr

def get_uniform_block(prog_id: str | ProgramType, name: str, *, programs: dict[str, ProgramType] = {}) -> UniformBlockType:
    """Get a uniform block from a program with proper typing.
    
    This is a type-safe alternative to program[name] which returns a union type.
    Raises TypeError if the attribute is not a UniformBlock.
    """
    if isinstance(prog_id, str):
        if prog_id not in programs:
            raise ValueError(f"Program with id '{prog_id}' does not exist.")
        prog_id = programs[prog_id]
    
    attr = prog_id[name]
    if not isinstance(attr, UniformBlockType):
        raise TypeError(f"'{name}' is {type(attr).__name__}, not a UniformBlock")
    return attr

def set_uniform_block_binding(prog_id: str | ProgramType, name: str, binding: int, *, programs: dict[str, ProgramType] = {}) -> None:
    """Set the binding point for a uniform block.
    
    Args:
        prog_id: Program or program ID string
        name: Name of the uniform block
        binding: Binding point (0-based integer)
        programs: Dictionary of programs if using string ID
    """
    block = get_uniform_block(prog_id, name, programs=programs)
    block.binding = binding

def get_pattr_value(prog_id: str | ProgramType, name: str, *, programs: dict[str, ProgramType] = {}) -> Number | pArray:
    attr = get_pattr(prog_id, name, programs=programs)
    if not isinstance(attr, UniformType):
        raise TypeError(f"'{name}' is {type(attr).__name__}, not a Uniform")
    if _is_array_uniform(attr):
        raise TypeError(f"Uniform '{name}' is an array; cannot use .value")
    return attr.value

def set_pattr_value(prog_id: str | ProgramType, name: str, value: Number | pArray, *, programs: dict[str, ProgramType] = {}, force_write: bool = False) -> None:
    attr = get_pattr(prog_id, name, programs=programs)

    if not isinstance(attr, UniformType):
        raise TypeError(f"'{name}' is {type(attr).__name__}, not a Uniform")

    use_write = force_write or _is_array_uniform(attr)
    if use_write:
        if isinstance(value, np.ndarray):
            data = value
        else:
            data = np.array(value, dtype="f4")

        attr.write(data.tobytes())
    else:
        attr.value = value

PI = np.pi
PI_HALF = np.pi / 2
PI_QUARTER = np.pi / 4
TAU = np.pi * 2
