from __future__ import annotations
from typing import Any, Callable, Literal
import pygame as pg
from e2D import *

KEY_MODE_PRESSED = 0
KEY_MODE_JUST_PRESSED = 1
KEY_MODE_JUST_RELEASED = 2

SCANCODES = {"":0,"backspace":8,"tab":9,"return":13,"escape":27,"space":32,"!":33,"\"":34,"#":35,"$":36,"%":37,"&":38,"'":39,"(":40,")":41,"*":42,"+":43,",":44,"-":45,".":46,"/":47,"0":48,"1":49,"2":50,"3":51,"4":52,"5":53,"6":54,"7":55,"8":56,"9":57,":":58,";":59,"<":60,"=":61,">":62,"?":63,"@":64,"[":91,"\\":92,"]":93,"^":94,"_":95,"`":96,"a":97,"b":98,"c":99,"d":100,"e":101,"f":102,"g":103,"h":104,"i":105,"j":106,"k":107,"l":108,"m":109,"n":110,"o":111,"p":112,"q":113,"r":114,"s":115,"t":116,"u":117,"v":118,"w":119,"x":120,"y":121,"z":122,"delete":127,"caps lock":1073741881,"f1":1073741882,"f2":1073741883,"f3":1073741884,"f4":1073741885,"f5":1073741886,"f6":1073741887,"f7":1073741888,"f8":1073741889,"f9":1073741890,"f10":1073741891,"f11":1073741892,"f12":1073741893,"print screen":1073741894,"scroll lock":1073741895,"break":1073741896,"insert":1073741897,"home":1073741898,"page up":1073741899,"end":1073741901,"page down":1073741902,"right":1073741903,"left":1073741904,"down":1073741905,"up":1073741906,"numlock":1073741907,"[/]":1073741908,"[*]":1073741909,"[-]":1073741910,"[+]":1073741911,"enter":1073741912,"[1]":1073741913,"[2]":1073741914,"[3]":1073741915,"[4]":1073741916,"[5]":1073741917,"[6]":1073741918,"[7]":1073741919,"[8]":1073741920,"[9]":1073741921,"[0]":1073741922,"[.]":1073741923,"power":1073741926,"equals":1073741927,"f13":1073741928,"f14":1073741929,"f15":1073741930,"help":1073741941,"menu":1073741942,"sys req":1073741978,"clear":1073741980,"euro":1073742004,"CurrencySubUnit":1073742005,"left ctrl":1073742048,"left shift":1073742049,"left alt":1073742050,"left meta":1073742051,"right ctrl":1073742052,"right shift":1073742053,"right alt":1073742054,"right meta":1073742055,"alt gr":1073742081,"AC Back":1073742094}
SCANCODES_NUMS = {SCANCODES[key]:i for i,key in enumerate(SCANCODES)}

NEW_FONT = lambda size, name="Arial", bold=False, italic=False: pg.font.SysFont(name, size, bold, italic)
FONT_ARIAL_16 = NEW_FONT(16, "Arial")
FONT_ARIAL_32 = NEW_FONT(32, "Arial")
FONT_ARIAL_64 = NEW_FONT(64, "Arial")


__LITERAL_PIVOT_POSITIONS__ = Literal["top_left", "top_center", "top_right", "center_left", "center_center", "center_right", "bottom_left", "bottom_center", "bottom_right"]
__PIVOT_POSITIONS_MULTIPLIER__ = dict(zip(("top_left", "top_center", "top_right", "center_left", "center_center", "center_right", "bottom_left", "bottom_center", "bottom_right"), (Vector2D(x,y) for y in [0, .5, 1] for x in [0, .5, 1])))


# INPUT_CELL_ASCII_TYPE = 0
# INPUT_CELL_ALPHANUM_TYPE = 1
# INPUT_CELL_ALPHA_TYPE = 2
# INPUT_CELL_NUM_TYPE = 3
# LITERAL_INPUT_CELL_TYPES = Literal[0,1,2,3]

class Mouse:
    def __init__(self, parent) -> None:
        self.parent = parent
        self.pressed :list= [False, False, False]
        self.just_pressed :list= [False, False, False]
        self.just_released :list= [False, False, False]
        self.last_frame_movement = V2z.copy()
        self.update()
    
    def set_position(self, new_position:Vector2D|V2) -> None:
        self.position = new_position
        pg.mouse.set_pos(new_position())
    
    def update(self) -> None:
        self.position = V2(*pg.mouse.get_pos()) # type: ignore
        self.last_frame_movement = V2(*pg.mouse.get_rel())
        last_pressed = self.pressed.copy()
        self.pressed = list(pg.mouse.get_pressed()) # type: ignore
        self.just_pressed = [self.pressed[i] and not last_pressed[i] for i in range(3)]
        self.just_released = [not self.pressed[i] and last_pressed[i] for i in range(3)]
    
    def draw(self) -> None:
        pg.draw.circle(self.parent.screen, (110, 0, 0), self.position(), 10) # type: ignore

class Keyboard:
    def __init__(self, parent) -> None:
        self.parent = parent
        self.__pressed__ :list= [False for _ in SCANCODES_NUMS]
        self.__just_pressed__ :list= [False for _ in SCANCODES_NUMS]
        self.__just_released__ :list= [False for _ in SCANCODES_NUMS]
        self.update()
    
    def update(self) -> None:
        tmp_pressed = pg.key.get_pressed()
        last_pressed = self.__pressed__.copy()
        self.__pressed__ :list= [tmp_pressed[i] for i in SCANCODES_NUMS] # type: ignore
        self.__just_pressed__ = [self.__pressed__[i] and not last_pressed[i] for i in range(len(SCANCODES_NUMS))]
        self.__just_released__ = [not self.__pressed__[i] and last_pressed[i] for i in range(len(SCANCODES_NUMS))]
    
    def get_key(self, scan_code:int, mode=KEY_MODE_PRESSED) -> bool:
        """
        # Check Key State

        ## Parameters:
            scan_code (int): The pygame code value of the key to check (e.g., pg.K_SPACE, pg.K_a, pg.K_LEFT, pg.K_RIGHT, etc.).
            mode (int): The mode to check the key state: KEY_MODE_PRESSED, KEY_MODE_JUST_PRESSED, or KEY_MODE_JUST_RELEASED. Default is KEY_MODE_PRESSED.

        ## Returns:
            bool: True if the specified key condition is met; otherwise, False.

        ## Example:
            keyboard = Keyboard(parent_object)
            keyboard.update()
            if keyboard.get_key(pg.KEY_SPACE, mode=KEY_MODE_JUST_PRESSED):
                print("Space key has just been pressed!")

        ## Explanation:
            The 'get_key' method is used to check the state of a specific key.

            It takes the 'scan_code' parameter, which represents the name of the key to check (e.g., pg.K_SPACE, pg.K_a, pg.K_LEFT, pg.K_RIGHT, etc.).

            The 'mode' parameter can be used to specify whether to check for 'KEY_MODE_PRESSED' (key is currently pressed), 'KEY_MODE_JUST_PRESSED' (key has just been pressed in the current frame), or 'KEY_MODE_JUST_RELEASED' (key has just been released in the current frame).

            The method returns True if the specified condition is met; otherwise, it returns False.

            Example usage is shown in the "Example" section above.
        """
        ll = self.__pressed__
        if mode == KEY_MODE_PRESSED:
            ll = self.__pressed__
        elif mode == KEY_MODE_JUST_PRESSED:
            ll = self.__just_pressed__
        elif mode == KEY_MODE_JUST_RELEASED:
            ll = self.__just_released__
        return ll[SCANCODES_NUMS[scan_code]]


class Utils:
    def __init__(self) -> None:
        self.rootEnv = None
        self.surface : pg.Surface
    def draw(self) -> None: pass
    def update(self) -> None: pass

class InputCell(Utils):
    def __init__(self,
                initial_value:str,
                position:Vector2D,
                size:Vector2D,
                prefix:str|None=None,
                text_color:tuple[int,int,int]|list[int]=(255,255,255),
                bg_color:None|tuple[int,int,int]|list[int]=None,
                border_color:None|tuple[int,int,int]|list[int]=(255,255,255),
                border_width:float=0,
                border_radius:int|list[int]|tuple[int,int,int,int]=-1,
                margin:Vector2D=Vector2D.zero(),
                pivot_position:__LITERAL_PIVOT_POSITIONS__="center_center",
                font:pg.font.Font=FONT_ARIAL_32,
                personalized_surface:pg.Surface|None=None,
                on_enter_pressed:Callable[[str], Any]=lambda full_text: ...,
                check_when_adding:Callable[[str], str]=lambda new_text: new_text) -> None:
        super().__init__()

        self.on_enter_pressed = on_enter_pressed
        self.check_when_adding = check_when_adding
        self.prefix = prefix if prefix != None else ""
    
        self.text_color = text_color
        self.font = font
        self.surface = personalized_surface
        self.bg_color = bg_color
        # size = Vector2D(*self.text_box.get_size()) + self.margin * 2
        self.size = size
        self.position = (position - size * __PIVOT_POSITIONS_MULTIPLIER__[pivot_position] + margin)
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
                    self.value += self.check_when_adding(event.text)
                elif event.type == pg.KEYDOWN and event.key == pg.K_BACKSPACE:
                    self.value = self.value[:-1]
            if self.rootEnv.keyboard.get_key(pg.K_DELETE):
                self.value = self.value[:-1]
            if self.rootEnv.keyboard.get_key(pg.K_RETURN, KEY_MODE_JUST_PRESSED):
                self.on_enter_pressed(self.value)
            if self.rootEnv.keyboard.get_key(pg.K_ESCAPE, KEY_MODE_JUST_PRESSED):
                self.rootEnv.selected_util = self if self.rootEnv.selected_util != self else None
            self.update_text()

    def update_text(self) -> None:
        self.text_box = self.font.render(self.prefix + self.value, True, self.text_color)
        if self.rootEnv != None and self.rootEnv.selected_util == self:
            # self.text_position = self.position + self.size * Vector2D(.85, .5) - Vector2D(*self.text_box.get_size()) * Vector2D(1, .5) - self.position
            self.text_position = self.position + self.size * .5 - Vector2D(*self.text_box.get_size()) * Vector2D(.5, .5) - self.position
        else:
            self.text_position = self.position + self.size * .5 - Vector2D(*self.text_box.get_size()) * Vector2D(.5, .5) - self.position
