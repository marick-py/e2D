# Screen Recording (WinRec) - Async Video Capture

High-performance asynchronous screen recording with F-key controls and real-time statistics.

## Installation

Screen recording requires OpenCV:

```bash
# Install with recording support
pip install e2D[rec]

# Or install OpenCV separately
pip install e2D opencv-python
```

## Quick Start

```python
from e2D import RootEnv, DefEnv

class MyApp(DefEnv):
    def update(self):
        pass
    
    def draw(self):
        pass

rootEnv = RootEnv(window_size=(1920, 1080), target_fps=60)
rootEnv.init(MyApp())

# Enable recording
rootEnv.init_rec(
    fps=30,                    # Video FPS
    draw_on_screen=True,       # Show stats overlay
    path='output.mp4'          # Output file
)

rootEnv.loop()
```

## Keyboard Controls

| Key | Action |
|-----|--------|
| **F9** | Pause/Resume recording |
| **F10** | Restart recording (clear buffer, reset timers) |
| **F12** | Take screenshot (PNG) |

## Features

### ✅ Asynchronous Encoding
- **Background thread** writes frames to disk
- **Zero impact** on render performance
- **120-frame buffer** (4 seconds at 30fps)

### ✅ Real-Time Statistics
- Recording FPS vs Target FPS
- Buffer usage and fill percentage
- Frames written/dropped
- Recording time vs application time

### ✅ Pause/Resume Support
- Pause recording without stopping the app
- Excluded time shown separately
- Resume without gaps in video

### ✅ Screenshots
- Instant PNG screenshots
- Auto-numbered filenames
- Independent of video recording

## Configuration

```python
rootEnv.init_rec(
    fps=30,                 # Video framerate (30, 60, etc.)
    draw_on_screen=True,    # Show overlay stats
    path='output.mp4'       # Output video path
)
```

### Recommended Settings

**High Quality (1080p@60fps)**
```python
rootEnv.init_rec(fps=60, path='high_quality.mp4')
```

**Standard Quality (1080p@30fps)**
```python
rootEnv.init_rec(fps=30, path='standard.mp4')
```

**Performance Mode (720p@30fps)**
```python
# Set window size smaller
rootEnv = RootEnv(window_size=(1280, 720), target_fps=60)
rootEnv.init_rec(fps=30, path='performance.mp4')
```

## Statistics Overlay

When `draw_on_screen=True`, shows:

```
[REC] RecFrames: 1234 | RecTime: 41.13s | AppTime: 45.67s
Buffer: 45/120 (37.5%, 1.5s) | WriteFPS: 29.8
Written: 1234 | Dropped: 0 | OptBuf: 60
[F9]Pause/Resume [F10]Restart [F12]Screenshot
```

**What it means:**
- **RecFrames**: Frames actually recorded (excludes paused time)
- **RecTime**: Duration of recorded video
- **AppTime**: Total application runtime
- **Buffer**: Frames waiting to be written (size/max, %, seconds)
- **WriteFPS**: Actual disk write speed
- **OptBuf**: Recommended buffer size based on performance
- **Dropped**: Frames lost due to full buffer

## Manual Control

```python
from e2D import RootEnv

# Access WinRec instance
recorder = rootEnv.recorder

# Manual controls
recorder.pause()              # Pause recording
recorder.resume()             # Resume recording
recorder.toggle_recording()   # Toggle pause/resume
recorder.restart()            # Restart (clear buffer)
recorder.take_screenshot('my_screenshot.png')  # Custom filename
recorder.quit()               # Stop and save
```

## Advanced Usage

### Recording Specific Scenes

```python
class MyApp(DefEnv):
    def __init__(self):
        self.recording_mode = False
    
    def update(self):
        # Start recording when entering special mode
        if entering_boss_fight:
            rootEnv.recorder.resume()
            self.recording_mode = True
        
        # Stop recording after event
        if boss_defeated:
            rootEnv.recorder.pause()
            self.recording_mode = False
```

### Custom Screenshot Timing

```python
class MyApp(DefEnv):
    def update(self):
        # Auto-screenshot on specific events
        if player_level_up:
            filename = f'levelup_{player_level}.png'
            rootEnv.recorder.take_screenshot(filename)
        
        if achievement_unlocked:
            filename = f'achievement_{achievement_id}.png'
            rootEnv.recorder.take_screenshot(filename)
```

### Performance Monitoring

```python
class MyApp(DefEnv):
    def update(self):
        recorder = rootEnv.recorder
        
        # Check if buffer is getting full
        buffer_percent = (recorder.frame_queue.qsize() / 
                         recorder.frame_queue.maxsize) * 100
        
        if buffer_percent > 80:
            print("Warning: Recording buffer 80% full!")
            print(f"Write FPS: {recorder.current_write_fps:.1f}")
            print(f"Target FPS: {recorder.fps}")
```

## Troubleshooting

### Buffer Fills Up / Dropped Frames

**Cause**: Disk write speed slower than recording speed

**Solutions**:
1. Lower recording FPS: `init_rec(fps=30)` instead of 60
2. Use faster storage (SSD)
3. Lower resolution (smaller window)
4. Close other disk-intensive applications

### Video File Won't Open

**Cause**: Recording not properly stopped

**Solution**: Always call `recorder.quit()` or close app properly

### Low Write FPS

**Cause**: Disk bottleneck or CPU encoding overhead

**Solutions**:
1. Use `mp4v` codec (already default)
2. Close background applications
3. Use SSD instead of HDD

### Out of Sync Audio/Video

**Cause**: e2D only records video (no audio)

**Solution**: Record audio separately and sync in video editor

## Technical Details

### Performance Impact

- **Frame capture**: ~0.5ms (framebuffer read)
- **Frame encoding**: 0ms (background thread)
- **Buffer memory**: ~450MB for 120 frames @ 1080p
- **Disk space**: ~30MB/min @ 1080p30fps

### Video Format

- **Codec**: MPEG-4 (mp4v)
- **Container**: MP4
- **Color**: RGB (converted from OpenGL)
- **Compression**: Standard MP4 compression

### Screenshot Format

- **Format**: PNG (lossless)
- **Naming**: `{video_name}_screenshot_XXXX.png`
- **Quality**: Full resolution, no compression loss

## Best Practices

1. **Test recording** before important sessions
2. **Monitor buffer usage** - keep below 50%
3. **Use SSD** for high-quality recording
4. **Lower FPS** if performance drops
5. **Close recording** properly to save file
6. **Backup important recordings** immediately

## Example: Gameplay Recording

```python
from e2D import RootEnv, DefEnv
import glfw

class GameRecorder(DefEnv):
    def __init__(self):
        self.recording = False
    
    def update(self):
        # Toggle recording with R key
        if rootEnv.keyboard.get_key(glfw.KEY_R, KeyState.JUST_PRESSED):
            if self.recording:
                rootEnv.recorder.pause()
                print("Recording paused")
            else:
                rootEnv.recorder.resume()
                print("Recording started")
            self.recording = not self.recording
        
        # Auto-screenshot on high score
        if new_high_score:
            rootEnv.recorder.take_screenshot(f'highscore_{score}.png')
    
    def draw(self):
        # Your game rendering
        pass

# Setup
rootEnv = RootEnv(window_size=(1920, 1080), target_fps=60)
rootEnv.init(GameRecorder())
rootEnv.init_rec(fps=30, path='gameplay.mp4')
rootEnv.loop()
```

---

[← Back to README](../README.md)
