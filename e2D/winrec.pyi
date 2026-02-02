from __future__ import annotations
from typing import Any

from typing import Optional
import numpy as np
import cv2
import threading
import queue

class WinRec:
    """Asynchronous screen recorder for ModernGL-based e2D applications."""
    
    rootEnv: Any
    path: str
    fps: int
    draw_on_screen: bool
    is_recording: bool
    screenshot_counter: int
    recording_frames: int
    pause_start_time: Optional[float]
    total_pause_duration: float
    video_writer: cv2.VideoWriter
    frame_buffer: np.ndarray
    frame_queue: queue.Queue
    running: bool
    frames_written: int
    frames_dropped: int
    write_start_time: float
    last_stat_update: float
    current_write_fps: float
    write_thread: threading.Thread
    
    def __init__(
        self,
        rootEnv: Any,
        fps: int = 30,
        draw_on_screen: bool = True,
        path: str = 'output.mp4'
    ) -> None: ...
    
    def _write_worker(self) -> None:
        """Background thread that writes frames to video file."""
        ...
    
    def handle_input(self) -> None:
        """Handle recording control keyboard inputs (F9-F12)."""
        ...
    
    def update(self) -> None:
        """Capture frame from ModernGL framebuffer and queue for writing."""
        ...
    
    def get_rec_seconds(self) -> float:
        """Get recorded time in seconds (excludes paused time)."""
        ...
    
    def draw(self) -> None:
        """Draw recording statistics overlay on screen."""
        ...
    
    def pause(self) -> None:
        """Pause recording (stop capturing frames)."""
        ...
    
    def resume(self) -> None:
        """Resume recording (continue capturing frames)."""
        ...
    
    def toggle_recording(self) -> None:
        """Toggle between pause and resume."""
        ...
    
    def restart(self) -> None:
        """Restart recording: clear buffer, reset all counters and timers, resume recording."""
        ...
    
    def clear_buffer(self) -> None:
        """Clear the frame queue and reset write statistics."""
        ...
    
    def take_screenshot(self, filename: Optional[str] = None) -> str:
        """Save current screen as PNG screenshot."""
        ...
    
    def quit(self) -> None:
        """Stop recording and release resources."""
        ...