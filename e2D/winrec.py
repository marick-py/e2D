from e2D.envs import *
import pygame as pg
import cv2
import numpy as np

class WinRec:
    def __init__(self, rootEnv:RootEnv, fps:int=30, path:str='output.mp4') -> None:
        self.rootEnv = rootEnv
        self.path = path
        self.fps = fps
        self.video_writer = cv2.VideoWriter(self.path, cv2.VideoWriter_fourcc(*'mp4v'), self.fps, self.rootEnv.screen_size()) #type: ignore
        self.reset()
    
    def reset(self) -> None:
        self.frames = []
    
    def update(self) -> None:
        frame = cv2.cvtColor(np.swapaxes(pg.surfarray.array3d(self.rootEnv.screen), 0, 1), cv2.COLOR_RGB2BGR)
        self.video_writer.write(frame)

    def draw(self) -> None:
        self.rootEnv.print(f"[cfps:{self.rootEnv.current_frame} || realtime:{round(self.rootEnv.current_frame/self.fps,2)} || apptime:{round(self.rootEnv.get_time_from_start(),2)}]", self.rootEnv.screen_size, fixed_sides=TEXT_FIXED_SIDES_BOTTOM_RIGHT)
    
    def quit(self) -> None:
        self.video_writer.release()

