#version 430
layout(local_size_x=64) in;

layout(std430, binding=1) buffer PointBuffer {
    vec2 points[];
};

uniform vec2 offset;
uniform int capacity;

void main() {
    uint id = gl_GlobalInvocationID.x;
    if (id >= capacity) return;
    
    points[id] += offset;
}
