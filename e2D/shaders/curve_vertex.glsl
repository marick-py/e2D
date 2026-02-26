#version 430
layout(std140, binding=0) uniform View {
    vec2 resolution;
    vec2 center;
    vec2 scale;
    float aspect;
} view;

in vec2 in_pos;

void main() {
    gl_Position = vec4((in_pos - view.center) * view.scale, 0.0, 1.0);
}
