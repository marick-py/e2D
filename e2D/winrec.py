from e2D.envs import *
import pygame as pg
import numpy as np
import cv2

class WinRec:
    def __init__(self, rootEnv:RootEnv, fps:int=30, path:str='output.mp4') -> None:
        self.rootEnv = rootEnv
        self.path = path
        self.fps = fps
        self.video_writer = cv2.VideoWriter(self.path, cv2.VideoWriter_fourcc(*'mp4v'), self.fps, self.rootEnv.screen_size()) #type: ignore
    
    def update(self) -> None:
        frame = cv2.cvtColor(np.swapaxes(pg.surfarray.array3d(self.rootEnv.screen), 0, 1), cv2.COLOR_RGB2BGR)
        self.video_writer.write(frame)
    
    def get_rec_seconds(self) -> float:
        return self.rootEnv.current_frame/self.fps

    def draw(self, draw_on_screen=False) -> None:
        text = f"[cfps:{self.rootEnv.current_frame} || realtime:{round(self.get_rec_seconds(),2)} || apptime:{round(self.rootEnv.runtime_seconds,2)}]"
        pg.display.set_caption(text)
        if draw_on_screen: self.rootEnv.print(text, self.rootEnv.screen_size, pivot_position='bottom_right')
    
    def quit(self) -> None:
        self.video_writer.release()

