#version 430

layout(std430, binding = 0) buffer Points {
    vec2 points[];
};

uniform vec2 resolution;
uniform float point_size;

void main() {
    vec2 pos = points[gl_VertexID];
    
    // Convert pixel coords to NDC
    vec2 ndc = (pos / resolution) * 2.0 - 1.0;
    ndc.y = -ndc.y;  // Flip Y
    
    gl_Position = vec4(ndc, 0.0, 1.0);
    gl_PointSize = point_size;
}
