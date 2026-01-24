#version 430

layout(local_size_x = 256) in;

layout(std430, binding = 0) buffer Points {
    vec2 points[];
};

layout(std430, binding = 1) buffer Velocities {
    vec2 velocities[];
};

uniform float deltaTime;
uniform vec2 bounds;
uniform int count;
uniform uint seed;

// Simple hash function for random number generation
uint hash(uint x) {
    x += (x << 10u);
    x ^= (x >> 6u);
    x += (x << 3u);
    x ^= (x >> 11u);
    x += (x << 15u);
    return x;
}

// Generate pseudo-random float in [0, 1]
float random(uint seed, uint index) {
    uint h = hash(seed + index * 747796405u);
    return float(h) / 4294967295.0;
}

void main() {
    uint gid = gl_GlobalInvocationID.x;
    
    if (gid >= count) return;
    
    // Clamp deltaTime to prevent huge spikes when window is moved
    float dt = min(deltaTime, 0.1);
    
    // Random movement
    float rx = random(seed, gid * 2) - 0.5;
    float ry = random(seed, gid * 2 + 1) - 0.5;
    
    // Update velocity with random acceleration
    velocities[gid] += vec2(rx, ry) * 2000.0 * dt;
    
    // Apply very light damping (98% retention per second)
    float damping = exp(-0.02 * dt);
    velocities[gid] *= damping;
    
    // Clamp velocity to prevent runaway
    float speed = length(velocities[gid]);
    if (speed > 500.0) {
        velocities[gid] = (velocities[gid] / speed) * 500.0;
    }
    
    // Update position
    points[gid] += velocities[gid] * dt;
    
    // Bounce off boundaries
    if (points[gid].x < 0.0) {
        points[gid].x = 0.0;
        velocities[gid].x = abs(velocities[gid].x);
    }
    if (points[gid].x > bounds.x) {
        points[gid].x = bounds.x;
        velocities[gid].x = -abs(velocities[gid].x);
    }
    if (points[gid].y < 0.0) {
        points[gid].y = 0.0;
        velocities[gid].y = abs(velocities[gid].y);
    }
    if (points[gid].y > bounds.y) {
        points[gid].y = bounds.y;
        velocities[gid].y = -abs(velocities[gid].y);
    }
}
