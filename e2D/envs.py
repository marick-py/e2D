from .utils import *
import pygame as pg

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
font_arial_16 = pg.font.SysFont("Arial", 16)
font_arial_32 = pg.font.SysFont("Arial", 32)
font_arial_64 = pg.font.SysFont("Arial", 64)
my_arial_font_size = lambda size: pg.font.SysFont("Arial", size)

class RootEnv:
    def __init__(self, screen_size:V2|Vector2D=V2(1920, 1080), vsync:bool=True, target_fps:int=60, show_fps=True, quit_on_key_pressed:None|int=pg.K_x, window_flag:int=0) -> None:
        self.quit = False
        self.screen_size :V2|Vector2D= screen_size
        self.screen = pg.display.set_mode(self.screen_size(), vsync=vsync, flags=window_flag)
        self.target_fps = target_fps
        self.show_fps = show_fps
        self.clock = pg.time.Clock()
        self.keyboard = Keyboard(self)
        self.mouse = Mouse(self)
        self.events :list= []
        self.background_color = rgb(0,0,0)
        self._quit_on_key_pressed = quit_on_key_pressed
    
    def init(self, sub_env) -> None:
        self.env = sub_env
    
    def clear(self) -> None:
        self.screen.fill(self.background_color) #type: ignore
    
    def print(self, text:str, position:V2|Vector2D, color:tuple[float,float,float]=(255,255,255), center_x:bool=False, center_y:bool=False, font:pg.font.Font=font_arial_32) -> None:
        text_box = font.render(text, True, color) #type: ignore
        w,h = text_box.get_size()
        if center_x: position.x -= w / 2
        if center_y: position.y -= h / 2
        self.screen.blit(text_box, position())

    def __draw__(self) -> None:
        self.clock.tick(self.target_fps)
        self.clear()
        if self.show_fps: self.print(str(round(self.clock.get_fps(),2)), self.screen_size * .01)

        self.env.draw()
        pg.display.update()
    
    def __update__(self) -> None:
        self.mouse.update()
        self.keyboard.update()
        self.env.update()

    def frame(self) -> None:
        self.__update__()
        self.__draw__()

        self.events = pg.event.get()
        for event in self.events:
            if event.type == pg.QUIT or ((event.type == pg.KEYDOWN and event.key == self._quit_on_key_pressed) if self._quit_on_key_pressed != None else False):
                self.quit = True

################################################################################################################################################################################################################################
################################################################################################################################################################################################################################

""" TODO
from e2D import *
import pygame as pg
import easygui
import uuid

pg.init()
pg.font.init()
myfont = pg.font.SysFont("Arial", 32)

DEFAULT_MOUSE_BUTTON_MODE = 0
OVER_MOUSE_BUTTON_MODE = 1
CLICKED_MOUSE_BUTTON_MODE = 2

CALLBACK_MODE_ON_PRESSED = 0
CALLBACK_MODE_ON_RELEASED = 1

class Button:
    def_side_border = .85
    def __init__(self,
                 parent,
                 text,
                 screen_ratio_position:V2,
                 screen_ratio_size:V2, 
                 text_color:tuple[int|float,int|float,int|float],
                 def_color:tuple[int|float,int|float,int|float],
                 over_color:tuple[int|float,int|float,int|float],
                 click_color:tuple[int|float,int|float,int|float],
                 callback,
                 border_color:tuple[int|float,int|float,int|float]=(255,255,255),
                 border_width:int|float=2,
                 corners:list[int|float]|int|float|None=10,
                 callback_mode=CALLBACK_MODE_ON_RELEASED,
                 font="Algerian",
                 font_downscale:float=1.0,
                 **callback_kwargs) -> None:
        self.parent :Env= parent
        self.text :str= text
        self.screen_ratio_size = screen_ratio_size  # ratio position is bot right
        self.screen_ratio_position = screen_ratio_position # ratio position is top left
        self.text_color = text_color
        self.callback = callback
        self.callback_kwargs = callback_kwargs
        self.def_color = def_color
        self.over_color = over_color
        self.click_color = click_color
        self.mouse_mode = DEFAULT_MOUSE_BUTTON_MODE
        self.font = font
        self.font_downscale = font_downscale
        self.callback_mode = callback_mode
        self.border_color = border_color
        self.border_width = border_width
        self.corners = corners
        self.update_screen_ratio_position()
    
    def update_screen_ratio_position(self) -> None:
        self.position = self.parent.screen_size * self.screen_ratio_position
        self.size = self.parent.screen_size * self.screen_ratio_size - self.parent.screen_size * self.screen_ratio_position
        self.set_box_and_text_size()
    
    def set_box_and_text_size(self) -> None:
        text_box = pg.font.SysFont(self.font, int(self.size.y)).render(self.text, True, self.text_color) #type: ignore
        text_box_size = V2(*text_box.get_rect()[2:])
        ratio = text_box_size.x / text_box_size.y
        self.font_size = min(self.size.x * self.def_side_border / ratio, self.size.y) * self.font_downscale
        self.text_box = pg.font.SysFont(self.font, int(self.font_size)).render(self.text, True, self.text_color) #type: ignore
        self.text_box_size = V2(*self.text_box.get_rect()[2:])

    def draw(self) -> None:
        color = self.def_color
        if self.mouse_mode == DEFAULT_MOUSE_BUTTON_MODE:
            color = self.def_color
        elif self.mouse_mode == OVER_MOUSE_BUTTON_MODE:
            color = self.over_color
        elif self.mouse_mode == CLICKED_MOUSE_BUTTON_MODE:
            color = self.click_color
        
        if self.corners == None:
            pg.draw.rect(self.parent.screen, color, self.position() + self.size()) #type: ignore
        elif isinstance(self.corners, int|float):
            pg.draw.rect(self.parent.screen, color, self.position() + self.size(), border_radius=self.corners) #type: ignore
        elif type(self.corners) == list:
            pg.draw.rect(self.parent.screen, color, self.position() + self.size(), border_top_left_radius=self.corners[0], border_top_right_radius=self.corners[1], border_bottom_left_radius=self.corners[2], border_bottom_right_radius=self.corners[3]) #type: ignore
        if self.border_width:
            if self.corners == None:
                pg.draw.rect(self.parent.screen, self.border_color, self.position() + self.size(), self.border_width) #type: ignore
            elif isinstance(self.corners, int|float):
                pg.draw.rect(self.parent.screen, self.border_color, self.position() + self.size(), self.border_width, border_radius=self.corners) #type: ignore
            elif type(self.corners) == list:
                pg.draw.rect(self.parent.screen, self.border_color, self.position() + self.size(), self.border_width, border_top_left_radius=self.corners[0], border_top_right_radius=self.corners[1], border_bottom_left_radius=self.corners[2], border_bottom_right_radius=self.corners[3]) #type: ignore
        
        self.parent.screen.blit(self.text_box, (self.position + (self.size - self.text_box_size) / 2)())

    def update(self) -> None:
        if self.position.x < self.parent.mouse.position.x < self.position.x + self.size.x and self.position.y < self.parent.mouse.position.y < self.position.y + self.size.y:
            if self.parent.mouse.just_pressed[0] and CALLBACK_MODE_ON_PRESSED or self.parent.mouse.just_released[0] and CALLBACK_MODE_ON_RELEASED:
                self.mouse_mode = CLICKED_MOUSE_BUTTON_MODE
                self.callback(**self.callback_kwargs)
            elif self.parent.mouse.pressed[0]:
                self.mouse_mode = CLICKED_MOUSE_BUTTON_MODE
            else:
                self.mouse_mode = OVER_MOUSE_BUTTON_MODE
        else:
            self.mouse_mode = DEFAULT_MOUSE_BUTTON_MODE


class ButtonCallBacks:
    def __init__(self, parent) -> None:
        self.parent :Env= parent

    def on_load_image_callback(self, **kwargs) -> None:
        path = easygui.fileopenbox(filetypes=["*.png"])
        if not path: return
        image = pg.image.load(path) #type: ignore
        self.parent.reference_images.append({"path": path, "image":image, "id": uuid.uuid4()})

class Env:
    def __init__(self) -> None:
        self.quit = False
        self.screen_size = V2(1920, 1080)
        self.screen = pg.display.set_mode(self.screen_size(), vsync=1, flags=pg.RESIZABLE)
        self.clock = pg.time.Clock()
        self.keyboard = Keyboard(self)
        self.mouse = Mouse(self)
        self.buttons_callbacks = ButtonCallBacks(self)
        self.buttons = [
            Button(self,
                   text="add photo path",
                   screen_ratio_position=V2(.75, .1),
                   screen_ratio_size=V2(.99, .25),
                   text_color=rgb(255, 255, 255),
                   def_color=rgb(194, 87, 0),
                   over_color=rgb(107, 57, 15),
                   click_color=rgb(32, 20, 9),
                   callback=self.buttons_callbacks.on_load_image_callback,
                   font_downscale=.9)
                   ]
        self.reference_images = []
    
    def print(self, text, position, color=(255,255,255)) -> None:
        text_box = myfont.render(text, True, color)
        self.screen.blit(text_box, position())

    def clear(self) -> None:
        self.screen.fill((0,0,0))
    
    def draw(self) -> None:
        self.clock.tick(0)
        self.clear()
        self.print(str(self.clock.get_fps()), self.screen_size * .01)

        for button in self.buttons: button.draw()
        self.mouse.draw()

        pg.display.update()
    
    def update(self) -> None:
        last_screen_size = self.screen_size()
        self.screen_size = V2(*self.screen.get_rect()[2:])
        if last_screen_size != self.screen_size():
            for button in self.buttons: button.update_screen_ratio_position()
        
        self.keyboard.update()
        self.mouse.update()
        for button in self.buttons: button.update()
    
    def frame(self) -> None:
        self.update()
        self.draw()

        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_x):
                self.quit = True

env = Env()

while not env.quit:
    env.frame()

"""