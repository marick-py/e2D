from __future__ import annotations
from typing import Literal

from .utils import *
import pygame as pg

"""  CODE EXAMPLE FOR RootEnv
from e2D.envs import *

class Env(DefEnv):
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

__LITERAL_PIVOT_POSITIONS__ = Literal["top_left", "top_center", "top_right", "center_left", "center_center", "center_right", "bottom_left", "bottom_center", "bottom_right"]
__PIVOT_POSITIONS_MULTIPLIER__ = dict(zip(("top_left", "top_center", "top_right", "center_left", "center_center", "center_right", "bottom_left", "bottom_center", "bottom_right"), (Vector2D(x,y) for y in [0, .5, 1] for x in [0, .5, 1])))

class DefEnv:
    def __init__(self) -> None: ...

    def draw(self) -> None: ...

    def update(self) -> None: ...

class RootEnv:
    def __init__(self,
                 screen_size : Vector2D = Vector2D(1920, 1080),
                 target_fps : int = 60,
                 show_fps = True,
                 quit_on_key_pressed : None|int = pg.K_x,
                 vsync : bool = True,
                 window_flag : int = 0,
                 clear_screen_each_frame : bool = True) -> None:
        self.quit = False
        self.__screen_size__ :Vector2D= screen_size

        self.__vsync__ = vsync
        self.__flags__ = window_flag
        self.screen = pg.display.set_mode(self.__screen_size__(), vsync=self.__vsync__, flags=self.__flags__)

        self.clock = pg.time.Clock()
        self.keyboard = Keyboard()
        self.mouse = Mouse(self)

        self.target_fps = target_fps
        self.current_fps = self.target_fps if self.target_fps != 0 else 1
        self.current_frame = 0
        self.show_fps = show_fps
        self.events :list[pg.event.Event]= []
        self.background_color = rgb(0,0,0)
        self.clear_screen_each_frame = clear_screen_each_frame
        self.utils :dict[int|str, Util]= {}
        self.selected_util :Util|None = None
        self.__quit_on_key_pressed__ = quit_on_key_pressed
    

    @property
    def screen_size(self) -> Vector2D:
        return self.__screen_size__

    @screen_size.setter
    def screen_size(self, new_size:Vector2D) -> None:
        self.screen = pg.display.set_mode(self.__screen_size__(), vsync=self.__vsync__, flags=self.__flags__)

    @property
    def delta(self) -> int:
        return self.clock.get_time()

    def get_teoric_max_fps(self) -> float:
        rawdelta = self.clock.get_rawtime()
        return (1000 / rawdelta) if rawdelta != 0 else 1
    
    def update_screen_mode(self, vsync:None|bool=None, flags=None) -> None:
        pass
    
    def sleep(self, seconds:int|float, precise_delay=False) -> None:
        if precise_delay:
            pg.time.delay(seconds * 1000)
        else:
            pg.time.wait(seconds * 1000)
    
    def add_utils(self, *utils:Util) -> None:
        for util in utils:
            if util.surface == None: util.surface = self.screen
            util.rootEnv = self
            self.utils[util.id] = util
    
    def remove_utils(self, *utils:int|str|Util) -> None:
        for uid in utils:
            if uid in self.utils:
                del self.utils[uid]
            elif isinstance(uid, Util):
                del self.utils[uid.id]
            else:
                raise Exception(f"Unknown util type: {uid}")
    
    @property
    def runtime_seconds(self) -> float:
        return pg.time.get_ticks()
    
    def init(self, sub_env:DefEnv) -> None:
        self.env = sub_env
    
    def clear(self) -> None:
        self.screen.fill(self.background_color)
    
    def clear_rect(self, position:Vector2D, size:Vector2D) -> None:
        self.screen.fill(self.background_color, position() + size())
    
    def print(self, 
            text : str, 
            position : Vector2D, 
            color : tuple[float,float,float] = (255,255,255), 
            pivot_position : __LITERAL_PIVOT_POSITIONS__ = "top_left",
            font : pg.font.Font = FONT_ARIAL_32,
            bg_color : None|tuple[int,int,int]|list[int] = None,
            border_color : None|tuple[int,int,int]|list[int] = (255,255,255),
            border_width : float = 0,
            border_radius : int|list[int]|tuple[int,int,int,int] = -1,
            margin : Vector2D = Vector2D.zero(),
            personalized_surface : pg.Surface|None = None
            ) -> None:
        text_box = font.render(text, True, color)
        size = Vector2D(*text_box.get_size()) + margin * 2
        pivotted_position = position - size * __PIVOT_POSITIONS_MULTIPLIER__[pivot_position] + margin
        if not any(isinstance(border_radius, cls) for cls in {tuple, list}): border_radius = [border_radius]*4
        surface = (self.screen if personalized_surface == None else personalized_surface)
        if bg_color != None:
            pg.draw.rect(surface, bg_color, (pivotted_position - margin)() + size(), 0, -1, *border_radius)
        if border_width:
            pg.draw.rect(surface, border_color, (pivotted_position - margin)() + size(), border_width, -1, *border_radius)
        surface.blit(text_box, pivotted_position())

    def __draw__(self) -> None:
        self.clock.tick(self.target_fps)
        self.current_fps = self.clock.get_fps()
        if self.clear_screen_each_frame: self.clear()
        if self.show_fps: self.print(str(round(self.current_fps,2)), self.screen_size * .01, bg_color=(0,0,0))
        
        self.env.draw()
        for util in self.utils.values(): util.draw()
        pg.display.update()
    
    def __update__(self) -> None:
        self.mouse.update()
        self.keyboard.update()
        self.env.update()
        for util in self.utils.values(): util.update()

    def frame(self) -> None:
        self.events = pg.event.get()
        self.current_frame += 1
        self.__update__()
        self.__draw__()

        for event in self.events:
            if event.type == pg.QUIT or ((event.type == pg.KEYDOWN and event.key == self.__quit_on_key_pressed__ and self.selected_util == None) if self.__quit_on_key_pressed__ != None else False):
                self.quit = True
