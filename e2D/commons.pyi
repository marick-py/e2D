"""
Type stubs for commons module
Common utility functions for moderngl programs
"""
from .types import ComputeShaderType, Number, ProgramAttrType, ProgramType, UniformBlockType, UniformType, pArray


def get_pattr(
    prog_id: str | ProgramType, 
    name: str, 
    *, 
    programs: dict[str, ProgramType] = {}
) -> ProgramAttrType:
    """Get a program attribute by name"""
    ...

def get_uniform(
    prog_id: str | ProgramType | ComputeShaderType, 
    name: str, 
    *, 
    compute_shaders: dict[str, ComputeShaderType] = {}, 
    programs: dict[str, ProgramType] = {}
) -> UniformType:
    """Get a uniform from a program or compute shader with proper typing.
    
    This is a type-safe alternative to program[name] which returns a union type.
    Raises TypeError if the attribute is not a Uniform.
    """
    ...

def get_uniform_block(
    prog_id: str | ProgramType,
    name: str,
    *,
    programs: dict[str, ProgramType] = {}
) -> UniformBlockType:
    """Get a uniform block from a program with proper typing.
    
    This is a type-safe alternative to program[name] which returns a union type.
    Raises TypeError if the attribute is not a UniformBlock.
    """
    ...

def set_uniform_block_binding(
    prog_id: str | ProgramType,
    name: str,
    binding: int,
    *,
    programs: dict[str, ProgramType] = {}
) -> None:
    """Set the binding point for a uniform block.
    
    Args:
        prog_id: Program or program ID string
        name: Name of the uniform block
        binding: Binding point (0-based integer)
        programs: Dictionary of programs if using string ID
    """
    ...

def get_pattr_value(
    prog_id: str | ProgramType, 
    name: str, 
    *, 
    programs: dict[str, ProgramType] = {}
) -> Number | pArray:
    """Get the value of a program uniform"""
    ...

def set_pattr_value(
    prog_id: str | ProgramType, 
    name: str, 
    value: Number | pArray, 
    *, 
    programs: dict[str, ProgramType] = {}, 
    force_write: bool = False
) -> None:
    """Set the value of a program uniform"""
    ...
