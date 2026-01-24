#version 430
uniform vec4 color;
uniform bool round_points;
out vec4 f_color;
void main() {
    if (round_points) {
        vec2 coord = gl_PointCoord - vec2(0.5);
        if (length(coord) > 0.5) discard;
    }
    f_color = color;
}
