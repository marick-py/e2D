#version 430
layout(std140, binding=0) uniform View {
    vec2 resolution;
    vec2 center;
    vec2 scale;
    float aspect;
} view;

layout(std430, binding=1) buffer PointBuffer {
    vec2 points[];
};

uniform int start_index;
uniform int capacity;
uniform float point_size;

void main() {
    // Handle ring buffer wrapping
    int idx = (start_index + gl_VertexID) % capacity;
    vec2 p = points[idx];
    
    vec2 diff = p - view.center;
    vec2 norm = diff * view.scale;
    norm.x /= view.aspect;
    gl_Position = vec4(norm, 0.0, 1.0);
    gl_PointSize = point_size;
}
