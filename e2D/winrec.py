from __future__ import annotations
from typing import Any, Optional
import numpy as np
import cv2
import threading
import queue
import time


class WinRec:
    """
    Asynchronous screen recorder for ModernGL-based e2D applications.
    
    Usage:
        rootEnv.init_rec(fps=30, draw_on_screen=True, path='output.mp4')
        # Recording happens automatically in the render loop
        # F9: Pause/Resume, F10: Restart, F12: Screenshot
    """
    
    def __init__(
        self,
        rootEnv: Any,
        fps: int = 30,
        draw_on_screen: bool = True,
        path: str = 'output.mp4'
    ) -> None:
        self.rootEnv = rootEnv
        self.path = path
        self.fps = fps
        self.draw_on_screen = draw_on_screen
        self.is_recording = True  # Recording state (pause/resume)
        self.screenshot_counter = 0  # Counter for screenshot filenames
        self.recording_frames = 0  # Frames actually recorded (excludes paused frames)
        self.pause_start_time: Optional[float] = None  # Track when recording was paused
        self.total_pause_duration = 0.0  # Cumulative pause time
        
        # Get window size
        width, height = self.rootEnv.window_size
        
        # Setup video writer
        self.video_writer = cv2.VideoWriter(
            self.path,
            cv2.VideoWriter_fourcc(*'mp4v'),  # type: ignore
            self.fps,
            (width, height)
        )
        
        # Pre-allocate buffers for zero-copy operations
        self.frame_buffer = np.empty(shape=(height, width, 3), dtype=np.uint8)
        
        # Setup async video writing
        self.frame_queue: queue.Queue = queue.Queue(maxsize=120)  # Buffer up to 4 seconds at 30fps
        self.running = True
        
        # Statistics tracking
        self.frames_written = 0
        self.frames_dropped = 0
        self.write_start_time = time.time()
        self.last_stat_update = time.time()
        self.current_write_fps = 0.0
        
        self.write_thread = threading.Thread(target=self._write_worker, daemon=False)
        self.write_thread.start()
    
    def _write_worker(self) -> None:
        """Background thread that writes frames to video file."""
        while self.running or not self.frame_queue.empty():
            try:
                frame = self.frame_queue.get(timeout=0.1)
                self.video_writer.write(frame)
                self.frames_written += 1
                self.frame_queue.task_done()
                
                # Update write FPS every second
                current_time = time.time()
                if current_time - self.last_stat_update >= 1.0:
                    elapsed = current_time - self.write_start_time
                    self.current_write_fps = self.frames_written / elapsed if elapsed > 0 else 0
                    self.last_stat_update = current_time
            except queue.Empty:
                continue
    
    def handle_input(self) -> None:
        """Handle recording control keyboard inputs (F9-F12)."""
        import glfw
        from .devices import KeyState
        
        # F9: Toggle pause/resume recording
        if self.rootEnv.keyboard.get_key(glfw.KEY_F9, KeyState.JUST_PRESSED):
            self.toggle_recording()
            status = "REC" if self.is_recording else "PAUSED"
            print(f"[Recording] {status}")
        
        # F10: Restart recording (reset all and resume)
        if self.rootEnv.keyboard.get_key(glfw.KEY_F10, KeyState.JUST_PRESSED):
            self.restart()
            print("[Recording] Restarted (buffer cleared, timers reset)")
        
        # F12: Take screenshot
        if self.rootEnv.keyboard.get_key(glfw.KEY_F12, KeyState.JUST_PRESSED):
            screenshot_path = self.take_screenshot()
            print(f"[Screenshot] Saved: {screenshot_path}")
    
    def update(self) -> None:
        """Capture frame from ModernGL framebuffer and queue for writing."""
        # Handle keyboard input first
        self.handle_input()
        
        # Skip frame capture if recording is paused
        if not self.is_recording:
            return
        
        # Increment recording frame counter
        self.recording_frames += 1
        
        # Read framebuffer from ModernGL context
        # Note: OpenGL reads bottom-to-top, so we need to flip
        width, height = self.rootEnv.window_size
        pixels = self.rootEnv.ctx.screen.read(components=3)
        
        # Convert bytes to numpy array and reshape
        frame = np.frombuffer(pixels, dtype=np.uint8).reshape((height, width, 3))
        
        # Flip vertically (OpenGL coordinates are bottom-up)
        frame = np.flipud(frame)
        
        # Convert RGB to BGR for OpenCV
        cv2.cvtColor(frame, cv2.COLOR_RGB2BGR, dst=self.frame_buffer)
        
        # Queue frame copy for async writing (non-blocking)
        try:
            self.frame_queue.put_nowait(self.frame_buffer.copy())
        except queue.Full:
            self.frames_dropped += 1  # Track dropped frames
    
    def get_rec_seconds(self) -> float:
        """Get recorded time in seconds (excludes paused time)."""
        return self.recording_frames / self.fps if self.fps > 0 else 0.0
    
    def draw(self) -> None:
        """Draw recording statistics overlay on screen."""
        if not self.draw_on_screen:
            return
        
        # Calculate statistics
        buffer_size = self.frame_queue.qsize()
        buffer_percent = (buffer_size / self.frame_queue.maxsize) * 100
        buffer_seconds = buffer_size / self.fps if self.fps > 0 else 0
        
        # Estimate optimal buffer size based on write performance
        if self.current_write_fps > 0 and self.fps > 0:
            write_lag = self.fps / self.current_write_fps
            estimated_buffer = int(self.fps * 2 * write_lag)  # 2 seconds of lag compensation
        else:
            estimated_buffer = self.frame_queue.maxsize
        
        # Recording state indicator
        rec_status = "REC" if self.is_recording else "PAUSED"
        
        # Format with fixed width for stable display
        from .text_renderer import TextStyle, Pivots
        from .color_defs import WHITE, BLACK
        
        row1 = (f"[{rec_status}] RecFrames:{self.recording_frames:>6} | "
                f"RecTime:{self.get_rec_seconds():>6.2f}s | "
                f"AppTime:{self.rootEnv.runtime:>6.2f}s")
        row2 = (f"Buffer:{buffer_size:>3}/{self.frame_queue.maxsize:<3} "
                f"({buffer_percent:>5.1f}%, {buffer_seconds:>4.1f}s) | "
                f"WriteFPS:{self.current_write_fps:>5.1f}")
        row3 = (f"Written:{self.frames_written:>6} | "
                f"Dropped:{self.frames_dropped:>4} | "
                f"OptBuf:{estimated_buffer:>3}")
        row4 = "[F9]Pause/Resume [F10]Restart [F12]Screenshot"
        
        # Position in bottom-right corner with spacing
        win_width, win_height = self.rootEnv.window_size_f
        x_pos = win_width - 16
        y_base = win_height - 16
        line_height = 30  # Approximate line height
        
        style = TextStyle(color=WHITE, bg_color=(0.0, 0.0, 0.0, 0.9))
        
        # Draw from bottom to top
        self.rootEnv.print(row4, (x_pos, y_base), style=style, pivot=Pivots.BOTTOM_RIGHT)
        self.rootEnv.print(row3, (x_pos, y_base - line_height), style=style, pivot=Pivots.BOTTOM_RIGHT)
        self.rootEnv.print(row2, (x_pos, y_base - line_height * 2), style=style, pivot=Pivots.BOTTOM_RIGHT)
        self.rootEnv.print(row1, (x_pos, y_base - line_height * 3), style=style, pivot=Pivots.BOTTOM_RIGHT)
    
    def pause(self) -> None:
        """Pause recording (stop capturing frames)."""
        if self.is_recording:
            self.is_recording = False
            self.pause_start_time = time.time()
    
    def resume(self) -> None:
        """Resume recording (continue capturing frames)."""
        if not self.is_recording and self.pause_start_time is not None:
            self.total_pause_duration += time.time() - self.pause_start_time
            self.pause_start_time = None
        self.is_recording = True
    
    def toggle_recording(self) -> None:
        """Toggle between pause and resume."""
        if self.is_recording:
            self.pause()
        else:
            self.resume()
    
    def restart(self) -> None:
        """Restart recording: clear buffer, reset all counters and timers, resume recording."""
        self.clear_buffer()
        self.recording_frames = 0
        self.total_pause_duration = 0.0
        self.pause_start_time = None
        self.is_recording = True
    
    def clear_buffer(self) -> None:
        """Clear the frame queue and reset write statistics."""
        # Clear the queue
        while not self.frame_queue.empty():
            try:
                self.frame_queue.get_nowait()
                self.frame_queue.task_done()
            except queue.Empty:
                break
        
        # Reset write counters (but keep recording frames)
        self.frames_written = 0
        self.frames_dropped = 0
        self.write_start_time = time.time()
        self.last_stat_update = time.time()
        self.current_write_fps = 0.0
    
    def take_screenshot(self, filename: Optional[str] = None) -> str:
        """
        Save current screen as PNG screenshot.
        
        Args:
            filename: Optional custom filename. If None, auto-generates with counter.
        
        Returns:
            str: Path to saved screenshot
        """
        if filename is None:
            # Auto-generate filename with counter
            base_path = self.path.rsplit('.', 1)[0]  # Remove .mp4 extension
            filename = f"{base_path}_screenshot_{self.screenshot_counter:04d}.png"
            self.screenshot_counter += 1
        
        # Capture current screen from ModernGL
        width, height = self.rootEnv.window_size
        pixels = self.rootEnv.ctx.screen.read(components=3)
        
        # Convert bytes to numpy array and reshape
        frame = np.frombuffer(pixels, dtype=np.uint8).reshape((height, width, 3))
        
        # Flip vertically (OpenGL coordinates are bottom-up)
        frame = np.flipud(frame)
        
        # Convert RGB to BGR for OpenCV
        screenshot_buffer = np.empty(shape=(height, width, 3), dtype=np.uint8)
        cv2.cvtColor(frame, cv2.COLOR_RGB2BGR, dst=screenshot_buffer)
        
        # Save as PNG
        cv2.imwrite(filename, screenshot_buffer)
        return filename
    
    def quit(self) -> None:
        """Stop recording and release resources."""
        # Stop accepting new frames and wait for queue to flush
        self.running = False
        self.frame_queue.join()  # Wait for all queued frames to be written
        self.write_thread.join(timeout=5.0)  # Wait for thread to finish
        self.video_writer.release()
        print(f"[Recording] Saved {self.frames_written} frames to {self.path}")
