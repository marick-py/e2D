#version 430

out vec4 color;

void main() {
    // Make circular points with smooth edges
    vec2 coord = gl_PointCoord * 2.0 - 1.0;
    float dist = length(coord);
    
    if (dist > 1.0) discard;
    
    float alpha = 1.0 - smoothstep(0.5, 1.0, dist);
    color = vec4(1.0, 1.0, 1.0, alpha);
}
