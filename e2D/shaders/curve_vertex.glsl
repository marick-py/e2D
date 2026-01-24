#version 430
layout(std140, binding=0) uniform View {
    vec2 resolution;
    vec2 center;
    vec2 scale;
    float aspect;
} view;

in vec2 in_pos;

void main() {
    vec2 diff = in_pos - view.center;
    vec2 norm = diff * view.scale;
    norm.x /= view.aspect;
    gl_Position = vec4(norm, 0.0, 1.0);
}
