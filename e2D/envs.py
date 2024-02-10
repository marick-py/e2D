from __future__ import annotations
from .utils import *
import pygame as pg
from time import time as __tm__

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
FONT_ARIAL_16 = pg.font.SysFont("Arial", 16)
FONT_ARIAL_32 = pg.font.SysFont("Arial", 32)
FONT_ARIAL_64 = pg.font.SysFont("Arial", 64)
create_arial_font_size = lambda size: pg.font.SysFont("Arial", size)

TEXT_FIXED_SIDES_TOP_LEFT = 0
TEXT_FIXED_SIDES_TOP_MIDDLE = 1
TEXT_FIXED_SIDES_TOP_RIGHT = 2
TEXT_FIXED_SIDES_MIDDLE_LEFT = 3
TEXT_FIXED_SIDES_MIDDLE_MIDDLE = 4
TEXT_FIXED_SIDES_MIDDLE_RIGHT = 5
TEXT_FIXED_SIDES_BOTTOM_LEFT = 6
TEXT_FIXED_SIDES_BOTTOM_MIDDLE = 7
TEXT_FIXED_SIDES_BOTTOM_RIGHT = 8

class RootEnv:
    __fixed_sides_multiplier = [V2(x,y) for y in [0, .5, 1] for x in [0, .5, 1]]
    def __init__(self, screen_size:V2|Vector2D=V2(1920, 1080), vsync:bool=True, target_fps:int=60, show_fps=True, quit_on_key_pressed:None|int=pg.K_x, window_flag:int=0, clear_screen_each_frame:bool=True) -> None:
        self.quit = False
        self.screen_size :V2|Vector2D= screen_size
        self.screen = pg.display.set_mode(self.screen_size(), vsync=vsync, flags=window_flag)
        self.target_fps = target_fps
        self.current_fps = self.target_fps if self.target_fps != 0 else 1
        self.delta = 1 / self.current_fps
        self.current_frame = 0
        self.show_fps = show_fps
        self.clock = pg.time.Clock()
        self.keyboard = Keyboard(self)
        self.mouse = Mouse(self)
        self.events :list= []
        self.background_color = rgb(0,0,0)
        self._quit_on_key_pressed = quit_on_key_pressed
        self.clear_screen_each_frame = clear_screen_each_frame
        self.starting_time = __tm__()
    
    def get_time_from_start(self) -> float:
        return __tm__() - self.starting_time
    
    def init(self, sub_env) -> None:
        self.env = sub_env
    
    def clear(self) -> None:
        self.screen.fill(self.background_color)
    
    def clear_rect(self, position:V2|Vector2D, size:V2|Vector2D) -> None:
        self.screen.fill(self.background_color, position() + size())
    
    def print(self, text:str, position:V2|Vector2D, color:tuple[float,float,float]=(255,255,255), fixed_sides=TEXT_FIXED_SIDES_TOP_LEFT, font:pg.font.Font=FONT_ARIAL_32, bg_color:None|tuple[int,int,int]|list[int]=None, border_color:None|tuple[int,int,int]|list[int]=None, border_width:float=0, border_radius:int|list[int]|tuple[int,int,int,int]=-1, margin:V2|Vector2D=V2z, personalized_surface:pg.Surface|None=None) -> None:
        text_box = font.render(text, True, color)
        size = V2(*text_box.get_size()) + margin * 2
        position = position - size * self.__fixed_sides_multiplier[fixed_sides] + margin
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
        pg.display.update()
    
    def __update__(self) -> None:
        self.mouse.update()
        self.keyboard.update()
        self.env.update()

    def frame(self) -> None:
        self.__update__()
        self.__draw__()

        self.current_frame += 1
        self.events = pg.event.get()
        for event in self.events:
            if event.type == pg.QUIT or ((event.type == pg.KEYDOWN and event.key == self._quit_on_key_pressed) if self._quit_on_key_pressed != None else False):
                self.quit = True