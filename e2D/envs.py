from __future__ import annotations
from typing import Any, Callable, Literal

from .utils import *
import pygame as pg
from pygame.event import Event
from time import time as __tm__
import math as _mt

"""  CODE EXAMPLE FOR RootEnv
from e2D.envs import *

class Env:
    def __init__(self) -> None:
        pass

    def draw(self) -> None:
        pass

    def update(self) -> None:
        pass

(rootEnv:=RootEnv()).init(Env())
while not rootEnv.quit:
    rootEnv.frame()
"""

pg.init()
pg.font.init()

class RootEnv:
    def __init__(self, screen_size:Vector2D=Vector2D(1920, 1080), vsync:bool=True, target_fps:int=60, show_fps=True, quit_on_key_pressed:None|int=pg.K_x, window_flag:int=0, clear_screen_each_frame:bool=True) -> None:
        self.quit = False
        self.screen_size :Vector2D= screen_size
        self.screen = pg.display.set_mode(self.screen_size(), vsync=vsync, flags=window_flag)
        self.target_fps = target_fps
        self.current_fps = self.target_fps if self.target_fps != 0 else 1
        self.delta = 1 / self.current_fps
        self.current_frame = 0
        self.show_fps = show_fps
        self.clock = pg.time.Clock()
        self.keyboard = Keyboard(self)
        self.mouse = Mouse(self)
        self.events :list[Event]= []
        self.background_color = rgb(0,0,0)
        self._quit_on_key_pressed = quit_on_key_pressed
        self.clear_screen_each_frame = clear_screen_each_frame
        self.starting_time :float= __tm__()
        self.utils :list[Utils]= []
        self.selected_util :Utils|None = None
    
    def add_utils(self, *utils:Utils) -> None:
        for util in utils:
            if util.surface == None: util.surface = self.screen
        util.rootEnv = self
        self.utils.extend(utils)
    
    def remove_utils(self, *utils:list[Utils]) -> None:
        for u in utils: self.utils.remove(u)
    
    def get_time_from_start(self) -> float:
        return __tm__() - self.starting_time
    
    def init(self, sub_env) -> None:
        self.env = sub_env
    
    def clear(self) -> None:
        self.screen.fill(self.background_color)
    
    def clear_rect(self, position:Vector2D, size:Vector2D) -> None:
        self.screen.fill(self.background_color, position() + size())
    
    def print(self, text:str, position:Vector2D, color:tuple[float,float,float]=(255,255,255), fixed_sides=TEXT_FIXED_SIDES_TOP_LEFT, font:pg.font.Font=FONT_ARIAL_32, bg_color:None|tuple[int,int,int]|list[int]=None, border_color:None|tuple[int,int,int]|list[int]=(255,255,255), border_width:float=0, border_radius:int|list[int]|tuple[int,int,int,int]=-1, margin:Vector2D=Vector2D.zero(), personalized_surface:pg.Surface|None=None) -> None:
        text_box = font.render(text, True, color)
        size = Vector2D(*text_box.get_size()) + margin * 2
        position = position - size * FIXED_SIDES_MULTIPLIER[fixed_sides] + margin
        if not any(isinstance(border_radius, cls) for cls in {tuple, list}): border_radius = [border_radius]*4
        surface = (self.screen if personalized_surface == None else personalized_surface)
        if bg_color != None:
            pg.draw.rect(surface, bg_color, (position - margin)() + size(), 0, -1, *border_radius)
        if border_width:
            pg.draw.rect(surface, border_color, (position - margin)() + size(), border_width, -1, *border_radius)
        surface.blit(text_box, position())

    def __draw__(self) -> None:
        self.clock.tick(self.target_fps)
        self.current_fps = self.clock.get_fps()
        self.delta = 1 / (self.current_fps if self.current_fps != 0 else 1)
        if self.clear_screen_each_frame: self.clear()
        if self.show_fps: self.print(str(round(self.current_fps,2)), self.screen_size * .01, bg_color=(0,0,0))
        
        self.env.draw()
        for util in self.utils: util.draw()
        pg.display.update()
    
    def __update__(self) -> None:
        self.mouse.update()
        self.keyboard.update()
        self.env.update()
        for util in self.utils: util.update()

    def frame(self) -> None:
        self.events = pg.event.get()
        self.current_frame += 1
        self.__update__()
        self.__draw__()

        for event in self.events:
            if event.type == pg.QUIT or ((event.type == pg.KEYDOWN and event.key == self._quit_on_key_pressed and self.selected_util == None) if self._quit_on_key_pressed != None else False):
                self.quit = True
