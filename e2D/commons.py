import moderngl
import numpy as np

def _is_array_uniform(u: moderngl.Uniform) -> bool:
    return u.array_length > 1

def get_pattr(prog_id:str|moderngl.Program, name:str, *, programs: dict[str, moderngl.Program]= {}) -> moderngl.Uniform | moderngl.UniformBlock | moderngl.Attribute | moderngl.Varying:
    if isinstance(prog_id, moderngl.Program):
        return prog_id[name]
    if prog_id not in programs:
        raise ValueError(f"Program with id '{prog_id}' does not exist.")
    return programs[prog_id][name]
    
def get_uniform(prog_id:str|moderngl.Program|moderngl.ComputeShader, name:str, *, compute_shaders: dict[str, moderngl.ComputeShader]= {}, programs: dict[str, moderngl.Program]= {}) -> moderngl.Uniform:
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
    if not isinstance(attr, moderngl.Uniform):
        raise TypeError(f"'{name}' is {type(attr).__name__}, not a Uniform")
    return attr

def get_pattr_value(prog_id:str|moderngl.Program, name:str, *, programs: dict[str, moderngl.Program]= {}) -> int|float|tuple|list:
    attr = get_pattr(prog_id, name, programs=programs)
    if not isinstance(attr, moderngl.Uniform):
        raise TypeError(f"'{name}' is {type(attr).__name__}, not a Uniform")
    if _is_array_uniform(attr):
        raise TypeError(f"Uniform '{name}' is an array; cannot use .value")
    return attr.value

def set_pattr_value(prog_id:str|moderngl.Program, name: str, value, *, programs: dict[str, moderngl.Program]= {}, force_write: bool= False) -> None:
    attr = get_pattr(prog_id, name, programs=programs)

    if not isinstance(attr, moderngl.Uniform):
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