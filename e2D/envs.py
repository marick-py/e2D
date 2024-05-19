from __future__ import annotations

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
FONT_ARIAL_16 = pg.font.SysFont("Arial", 16)
FONT_ARIAL_32 = pg.font.SysFont("Arial", 32)
FONT_ARIAL_64 = pg.font.SysFont("Arial", 64)
new_font = lambda size, name="Arial", bold=False, italic=False: pg.font.SysFont(name, size, bold, italic)

TEXT_FIXED_SIDES_TOP_LEFT = 0
TEXT_FIXED_SIDES_TOP_MIDDLE = 1
TEXT_FIXED_SIDES_TOP_RIGHT = 2
TEXT_FIXED_SIDES_MIDDLE_LEFT = 3
TEXT_FIXED_SIDES_MIDDLE_MIDDLE = 4
TEXT_FIXED_SIDES_MIDDLE_RIGHT = 5
TEXT_FIXED_SIDES_BOTTOM_LEFT = 6
TEXT_FIXED_SIDES_BOTTOM_MIDDLE = 7
TEXT_FIXED_SIDES_BOTTOM_RIGHT = 8

FIXED_SIDES_MULTIPLIER = [V2(x,y) for y in [0, .5, 1] for x in [0, .5, 1]]

INPUT_CELL_ASCII_TYPE = 0
INPUT_CELL_ALPHANUM_TYPE = 1
INPUT_CELL_ALPHA_TYPE = 2
INPUT_CELL_NUM_TYPE = 3

class Utils:
    def __init__(self) -> None:
        self.rootEnv : RootEnv = None # type: ignore
        self.surface : pg.Surface
    def draw(self) -> None: pass
    def update(self) -> None: pass

class InputCell(Utils):
    def __init__(self,
                initial_value:str,
                position:V2|Vector2D,
                size:V2|Vector2D,
                prefix:str|None=None,
                text_color:tuple[int,int,int]|list[int]=(255,255,255),
                bg_color:None|tuple[int,int,int]|list[int]=None,
                border_color:None|tuple[int,int,int]|list[int]=(255,255,255),
                border_width:float=0,
                border_radius:int|list[int]|tuple[int,int,int,int]=-1,
                margin:V2|Vector2D=V2z,
                fixed_sides:int=TEXT_FIXED_SIDES_MIDDLE_MIDDLE,
                font:pg.font.Font=FONT_ARIAL_32,
                personalized_surface:pg.Surface|None=None,
                on_enter_pressed=None,
                check_when_adding=None) -> None:
        super().__init__()

        self.on_enter_pressed = on_enter_pressed
        self.check_when_adding = check_when_adding
        self.prefix = prefix if prefix != None else ""
    
        self.text_color = text_color
        self.font = font
        self.surface = personalized_surface
        self.bg_color = bg_color
        # size = V2(*self.text_box.get_size()) + self.margin * 2
        self.size = size
        self.position = (position - size * FIXED_SIDES_MULTIPLIER[fixed_sides] + margin)
        self.bg_rect = [0, 0] + size()
        self.margin_rect = (margin * -1)() + size()
        self.border_color = border_color
        self.border_radius = [border_radius]*4 if not any(isinstance(border_radius, cls) for cls in {tuple, list}) else border_radius
        self.border_width = border_width

        self.value = initial_value
        self.update_text()

        self.text_surface = pg.Surface(self.size(), pg.SRCALPHA, 32).convert_alpha()
        
    def draw(self) -> None:
        self.text_surface.fill((0,0,0,0))
        if self.bg_color != None:
            pg.draw.rect(self.text_surface, self.bg_color, self.bg_rect, 0, -1, *self.border_radius)
        
        self.text_surface.blit(self.text_box, self.text_position())
        
        if self.rootEnv.selected_util != self:
            if self.border_width:
                pg.draw.rect(self.text_surface, self.border_color, self.margin_rect, self.border_width, -1, *self.border_radius)
        else:
            pg.draw.rect(self.text_surface, [127 + 127 * _mt.sin(self.rootEnv.get_time_from_start() * 10)]*3, self.margin_rect, self.border_width if self.border_width else 10, -1, *self.border_radius)

        self.surface.blit(self.text_surface, self.position())
        
    def update(self) -> None:
        if self.rootEnv.mouse.just_pressed[0]:
            if self.position.x < self.rootEnv.mouse.position.x < self.position.x + self.size.x and\
               self.position.y < self.rootEnv.mouse.position.y < self.position.y + self.size.y:
                self.rootEnv.selected_util = self if self.rootEnv.selected_util != self else None
                self.update_text()
        if self.rootEnv.selected_util == self:
            for event in self.rootEnv.events:
                if event.type == pg.TEXTINPUT:
                    self.value += event.text if self.check_when_adding == None else self.check_when_adding(event.text)
                elif event.type == pg.KEYDOWN and event.key == pg.K_BACKSPACE:
                    self.value = self.value[:-1]
            if self.rootEnv.keyboard.get_key(pg.K_DELETE):
                self.value = self.value[:-1]
            if self.rootEnv.keyboard.get_key(pg.K_RETURN, KEY_MODE_JUST_PRESSED):
                if callable(self.on_enter_pressed): self.on_enter_pressed(self.value)
            if self.rootEnv.keyboard.get_key(pg.K_ESCAPE, KEY_MODE_JUST_PRESSED):
                self.rootEnv.selected_util = self if self.rootEnv.selected_util != self else None
            self.update_text()

    def update_text(self) -> None:
        self.text_box = self.font.render(self.prefix + self.value, True, self.text_color)
        if self.rootEnv != None and self.rootEnv.selected_util == self:
            # self.text_position = self.position + self.size * V2(.85, .5) - V2(*self.text_box.get_size()) * V2(1, .5) - self.position
            self.text_position = self.position + self.size * .5 - V2(*self.text_box.get_size()) * V2(.5, .5) - self.position
        else:
            self.text_position = self.position + self.size * .5 - V2(*self.text_box.get_size()) * V2(.5, .5) - self.position

class RootEnv:
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
    
    def clear_rect(self, position:V2|Vector2D, size:V2|Vector2D) -> None:
        self.screen.fill(self.background_color, position() + size())
    
    def print(self, text:str, position:V2|Vector2D, color:tuple[float,float,float]=(255,255,255), fixed_sides=TEXT_FIXED_SIDES_TOP_LEFT, font:pg.font.Font=FONT_ARIAL_32, bg_color:None|tuple[int,int,int]|list[int]=None, border_color:None|tuple[int,int,int]|list[int]=(255,255,255), border_width:float=0, border_radius:int|list[int]|tuple[int,int,int,int]=-1, margin:V2|Vector2D=V2z, personalized_surface:pg.Surface|None=None) -> None:
        text_box = font.render(text, True, color)
        size = V2(*text_box.get_size()) + margin * 2
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
