#version 430
uniform vec2 resolution;
in vec2 in_pos;
void main() {
    // Convert pixel coords to NDC
    vec2 ndc = (in_pos / resolution) * 2.0 - 1.0;
    ndc.y = -ndc.y; // Flip Y
    gl_Position = vec4(ndc, 0.0, 1.0);
}
