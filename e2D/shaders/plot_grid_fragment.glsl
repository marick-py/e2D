#version 430
layout(std140, binding=0) uniform View {
    vec2 resolution;
    vec2 center;
    vec2 scale;
    float aspect;
} view;

uniform vec4 grid_color;
uniform vec4 axis_color;
uniform float spacing;
uniform bool show_grid;
uniform bool show_axis;

in vec2 uv;
out vec4 color;

void main() {
    // Calculate world position
    vec2 ndc = uv * 2.0 - 1.0;
    ndc.x *= view.aspect;
    vec2 world_pos = (ndc / view.scale) + view.center;
    
    vec4 final_color = vec4(0.0);
    
    // Grid
    if (show_grid) {
        vec2 grid = abs(fract(world_pos / spacing - 0.5) - 0.5) / (length(vec2(dFdx(world_pos.x/spacing), dFdy(world_pos.y/spacing))));
        float line = min(grid.x, grid.y);
        float alpha = 1.0 - smoothstep(0.0, 1.5, line);
        if (alpha > 0.0) {
            final_color = mix(final_color, grid_color, alpha);
        }
    }
    
    // Axis
    if (show_axis) {
        vec2 axis = abs(world_pos) / (length(vec2(dFdx(world_pos.x), dFdy(world_pos.y))));
        float axis_line = min(axis.x, axis.y);
        float axis_alpha = 1.0 - smoothstep(0.0, 2.0, axis_line);
        if (axis_alpha > 0.0) {
            final_color = mix(final_color, axis_color, axis_alpha);
        }
    }
    
    if (final_color.a <= 0.0) discard;
    color = final_color;
}
