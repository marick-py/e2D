#version 430

// Per-vertex attributes (quad corners: 4 vertices per instance)
in vec2 in_quad_pos;  // (-1,-1), (1,-1), (1,1), (-1,1)

// Per-instance attributes
in vec2 in_start;
in vec2 in_end;
in float in_width;
in vec4 in_color;

out vec4 v_color;

uniform vec2 resolution;

void main() {
    // Calculate line direction and perpendicular
    vec2 line_vec = in_end - in_start;
    float line_length = length(line_vec);
    vec2 line_dir = line_vec / line_length;
    vec2 line_perp = vec2(-line_dir.y, line_dir.x);
    
    // Calculate half-width
    float half_width = in_width * 0.5;
    
    // Expand quad along line direction and perpendicular
    vec2 world_pos = in_start + 
                     line_dir * (in_quad_pos.x * line_length * 0.5 + line_length * 0.5) +
                     line_perp * (in_quad_pos.y * half_width);
    
    // Convert to NDC
    vec2 ndc = (world_pos / resolution) * 2.0 - 1.0;
    ndc.y = -ndc.y;
    
    gl_Position = vec4(ndc, 0.0, 1.0);
    v_color = in_color;
}
