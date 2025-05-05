from __future__ import annotations
from typing import Any, Callable, Literal
import pygame as pg
from e2D import *
from e2D.colors import *

import math as _mt

pg.font.init()

__KEY_MODE_TYPES_DICT__ = dict(zip(["pressed", "just_pressed", "just_released"], range(3)))
__LITERAL_KEY_MODE_TYPES__ = Literal["pressed", "just_pressed", "just_released"]

__LITERAL_FONTS__ = Literal['arial', 'arialblack', 'bahnschrift', 'calibri', 'cambria', 'cambriamath', 'candara', 'comicsansms', 'consolas', 'constantia', 'corbel', 'couriernew', 'ebrima', 'franklingothicmedium', 'gabriola', 'gadugi', 'georgia', 'impact', 'inkfree', 'javanesetext', 'leelawadeeui', 'leelawadeeuisemilight', 'lucidaconsole', 'lucidasans', 'malgungothic', 'malgungothicsemilight', 'microsofthimalaya', 'microsoftjhenghei', 'microsoftjhengheiui', 'microsoftnewtailue', 'microsoftphagspa', 'microsoftsansserif', 'microsofttaile', 'microsoftyahei', 'microsoftyaheiui', 'microsoftyibaiti', 'mingliuextb', 'pmingliuextb', 'mingliuhkscsextb', 'mongolianbaiti', 'msgothic', 'msuigothic', 'mspgothic', 'mvboli', 'myanmartext', 'nirmalaui', 'nirmalauisemilight', 'palatinolinotype', 'segoemdl2assets', 'segoeprint', 'segoescript', 'segoeui', 'segoeuiblack', 'segoeuiemoji', 'segoeuihistoric', 'segoeuisemibold', 'segoeuisemilight', 'segoeuisymbol', 'simsun', 'nsimsun', 'simsunextb', 'sitkasmall', 'sitkatext', 'sitkasubheading', 'sitkaheading', 'sitkadisplay', 'sitkabanner', 'sylfaen', 'symbol', 'tahoma', 'timesnewroman', 'trebuchetms', 'verdana', 'webdings', 'wingdings', 'yugothic', 'yugothicuisemibold', 'yugothicui', 'yugothicmedium', 'yugothicuiregular', 'yugothicregular', 'yugothicuisemilight', 'holomdl2assets', 'bizudgothic', 'bizudpgothictruetype', 'bizudminchomedium', 'bizudpminchomediumtruetype', 'meiryo', 'meiryoui', 'msmincho', 'mspmincho', 'uddigikyokashonb', 'uddigikyokashonpb', 'uddigikyokashonkb', 'uddigikyokashonr', 'uddigikyokashonpr', 'uddigikyokashonkr', 'yumincho', 'lcd', 'glassgauge', 'maiandragd', 'maiandragddemi', 'newsgothic', 'quartz', 'kievitoffcpro', 'agencyfbgrassetto', 'agencyfb', 'algerian', 'bookantiquagrassetto', 'bookantiquagrassettocorsivo', 'bookantiquacorsivo', 'arialcorsivo', 'arialrounded', 'baskervilleoldface', 'bauhaus93', 'bell', 'bellgrassetto', 'bellcorsivo', 'bernardcondensed', 'bookantiqua', 'bodonigrassetto', 'bodonigrassettocorsivo', 'bodoniblackcorsivo', 'bodoniblack', 'bodonicondensedgrassetto', 'bodonicondensedgrassettocorsivo', 'bodonicondensedcorsivo', 'bodonicondensed', 'bodonicorsivo', 'bodonipostercompressed', 'bodoni', 'bookmanoldstyle', 'bookmanoldstylegrassetto', 'bookmanoldstylegrassettocorsivo', 'bookmanoldstylecorsivo', 'bradleyhanditc', 'britannic', 'berlinsansfbgrassetto', 'berlinsansfbdemigrassetto', 'berlinsansfb', 'broadway', 'brushscriptcorsivo', 'bookshelfsymbol7', 'californianfbgrassetto', 'californianfbcorsivo', 'californianfb', 'calisto', 'calistograssetto', 'calistograssettocorsivo', 'calistocorsivo', 'castellar', 'centuryschoolbook', 'centaur', 'century', 'chiller', 'colonna', 'cooperblack', 'copperplategothic', 'curlz', 'dubai', 'dubaimedium', 'dubairegular', 'elephant', 'elephantcorsivo', 'engravers', 'erasitc', 'erasdemiitc', 'erasmediumitc', 'felixtitling', 'forte', 'franklingothicbook', 'franklingothicbookcorsivo', 'franklingothicdemi', 'franklingothicdemicond', 'franklingothicdemicorsivo', 'franklingothicheavy', 'franklingothicheavycorsivo', 'franklingothicmediumcond', 'freestylescript', 'frenchscript', 'footlight', 'garamond', 'garamondgrassetto', 'garamondcorsivo', 'gigi', 'gillsansgrassettocorsivo', 'gillsansgrassetto', 'gillsanscondensed', 'gillsanscorsivo', 'gillsansultracondensed', 'gillsansultra', 'gillsans', 'gloucesterextracondensed', 'gillsansextcondensed', 'centurygothic', 'centurygothicgrassetto', 'centurygothicgrassettocorsivo', 'centurygothiccorsivo', 'goudyoldstyle', 'goudyoldstylegrassetto', 'goudyoldstylecorsivo', 'goudystout', 'harlowsolid', 'harrington', 'haettenschweiler', 'hightowertext', 'hightowertextcorsivo', 'imprintshadow', 'informalroman', 'blackadderitc', 'kristenitc', 'jokerman', 'juiceitc', 'kunstlerscript', 'widelatin', 'lucidabright', 'lucidacalligraphy', 'leelawadee', 'leelawadeegrassetto', 'lucidafax', 'lucidafaxdemigrassetto', 'lucidafaxdemigrassettocorsivo', 'lucidafaxcorsivo', 'lucidahandwritingcorsivo', 'lucidasansdemigrassetto', 'lucidasansdemigrassettocorsivo', 'lucidasanscorsivo', 'lucidasanstypewriter', 'lucidasanstypewritergrassetto', 'lucidasanstypewritergrassettooblique', 'lucidasanstypewriteroblique', 'magnetograssetto', 'maturascriptcapitals', 'mistral', 'modernno20', 'microsoftuighurgrassetto', 'microsoftuighur', 'monotypecorsiva', 'extra', 'niagaraengraved', 'niagarasolid', 'ocraextended', 'oldenglishtext', 'onyx', 'msoutlook', 'palacescript', 'papyrus', 'parchment', 'perpetuagrassettocorsivo', 'perpetuagrassetto', 'perpetuacorsivo', 'perpetuatitlinggrassetto', 'perpetuatitlingchiarissimo', 'perpetua', 'playbill', 'poorrichard', 'pristina', 'rage', 'ravie', 'msreferencesansserif', 'msreferencespecialty', 'rockwellcondensedgrassetto', 'rockwellcondensed', 'rockwell', 'rockwellgrassetto', 'rockwellgrassettocorsivo', 'rockwellextra', 'rockwellcorsivo', 'centuryschoolbookgrassetto', 'centuryschoolbookgrassettocorsivo', 'centuryschoolbookcorsivo', 'script', 'showcardgothic', 'snapitc', 'stencil', 'twcengrassettocorsivo', 'twcengrassetto', 'twcencondensedgrassetto', 'twcencondensedextra', 'twcencondensed', 'twcencorsivo', 'twcen', 'tempussansitc', 'vinerhanditc', 'vivaldicorsivo', 'vladimirscript', 'wingdings2', 'wingdings3', 'cascadiacoderegular', 'cascadiamonoregular', 'edwardianscriptitcnormale', 'stoneharbourregular', 'mregular', 'xirodregular', 'minecraft']

def NEW_FONT(size, name:__LITERAL_FONTS__="arial", bold:bool=False, italic:bool=False) -> pg.font.Font:
    return pg.font.SysFont(name, size, bold, italic)
FONT_ARIAL_16 = NEW_FONT(16)
FONT_ARIAL_32 = NEW_FONT(32)
FONT_ARIAL_64 = NEW_FONT(64)


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
        self.__last_frame_position_count__ = 0
        self.__last_frame_position__ = Vector2D.new_zero()
        self.__last_frame_movement_count__ = 0
        self.__last_frame_movement__ = Vector2D.new_zero()
        
        self.__pressed__ : tuple[bool, bool, bool] = (False, False, False)
        self.update()    

    @property
    def position(self) -> Vector2D:
        if self.__last_frame_position_count__ != self.parent.current_frame:
            self.__last_frame_position__ = Vector2D(*pg.mouse.get_pos())
            self.__last_frame_position_count__ = self.parent.current_frame
        return self.__last_frame_position__
    @position.setter
    def position(self, new_position:Vector2D) -> None:
        self.__last_frame_position_count__ = self.parent.current_frame
        self.__last_frame_position__ = new_position
        pg.mouse.set_pos(self.__last_frame_position__())
    
    @property
    def last_frame_movement(self) -> Vector2D:
        if self.__last_frame_movement_count__ != self.parent.current_frame:
            self.__last_frame_movement__ = Vector2D(*pg.mouse.get_rel())
            self.__last_frame_movement_count__ = self.parent.current_frame
        return self.__last_frame_movement__

    def update(self) -> None:
        self.__last_pressed__ = self.__pressed__
        self.__pressed__ = pg.mouse.get_pressed()

    def get_key(self, button_id:Literal[0,1,2]=0, mode:__LITERAL_KEY_MODE_TYPES__="pressed") -> bool:
        if mode == "pressed":
            return self.__pressed__[button_id]
        elif mode == "just_pressed":
            return self.__pressed__[button_id] and (not self.__last_pressed__[button_id])
        elif mode == "just_released":
            return (not self.__pressed__[button_id]) and self.__last_pressed__[button_id]
        else:
            raise Exception(f"Unknown mode type: {mode}")

class Keyboard:
    def __init__(self) -> None:
        self.__pressed__ :pg.key.ScancodeWrapper= pg.key.get_pressed()
        self.update()
    
    def update(self) -> None:
        self.__last_pressed__ = self.__pressed__
        self.__pressed__ = pg.key.get_pressed()
    
    def get_key(self, scan_code:int, mode:__LITERAL_KEY_MODE_TYPES__="pressed") -> bool:
        if mode == "pressed":
            return self.__pressed__[scan_code]
        elif mode == "just_pressed":
            return self.__pressed__[scan_code] and (not self.__last_pressed__[scan_code])
        elif mode == "just_released":
            return (not self.__pressed__[scan_code]) and self.__last_pressed__[scan_code]
        else:
            raise Exception(f"Unknown mode type: {mode}")

class Util:
    def __init__(self) -> None:
        self.rootEnv = None
        self.surface : pg.Surface = pg.SurfaceType
        self.id : int|str
        self.is_hovered :bool= False
        self.hidden :bool= False
    def hide(self) -> None:
        self.hidden = True
    def show(self) -> None:
        self.hidden = False
    def render(self) -> None: pass
    def draw(self) -> None: pass
    def update(self) -> None: pass

class InputCell(Util):
    def __init__(self,
                 initial_value : str,
                 position : Vector2D,
                 size : Vector2D,
                 prefix : str|None = None,
                 text_color : Color|pg.Color = Color.white(),
                 bg_color : None|Color|pg.Color = None,
                 border_color : Color|pg.Color = Color.white(),
                 border_width : float = 0,
                 border_radius : int|list[int]|tuple[int,int,int,int] = -1,
                 margin : Vector2D = Vector2D.zero(),
                 pivot_position : __LITERAL_PIVOT_POSITIONS__ = "center_center",
                 font : pg.font.Font = FONT_ARIAL_32,
                 personalized_surface : pg.Surface|None = None,
                 on_enter_pressed : Callable[[str], Any] = lambda full_text: ...,
                 check_when_adding : Callable[[str], str] = lambda new_text: new_text,
                ) -> None:
        super().__init__()
        
        self.value = initial_value

        # size = Vector2D(*self.text_box.get_size()) + self.margin * 2
        self.size = size
        self.position = (position - size * __PIVOT_POSITIONS_MULTIPLIER__[pivot_position] + margin)

        self.prefix = prefix if prefix != None else ""
    
        self.font = font
        
        self.bg_rect = [0, 0] + size()
        
        self.border_radius = [border_radius]*4 if not any(isinstance(border_radius, cls) for cls in {tuple, list}) else border_radius
        self.border_width = border_width
        
        self.margin_rect = (margin * -1)() + size()

        self.on_enter_pressed = on_enter_pressed
        self.check_when_adding = check_when_adding
        
        self.update_text()

        self.surface = personalized_surface
        self.text_surface = pg.Surface(self.size(), pg.SRCALPHA, 32).convert_alpha()
    
        self.text_color = text_color
        self.bg_color = bg_color
        self.border_color = border_color
        
    @property
    def text_color(self) -> Color:
        return unpygamize_color(self.__text_color__)
    @text_color.setter
    def text_color(self, new_color:Color|pg.Color) -> None:
        self.__text_color__ = pygamize_color(new_color)
    @property
    def bg_color(self) -> Color|None:
        return unpygamize_color(self.__bg_color__) if self.__bg_color__ else None
    @bg_color.setter
    def bg_color(self, new_color:Color|pg.Color|None) -> None:
        self.__bg_color__ = pygamize_color(new_color) if new_color else None
    @property
    def border_color(self) -> Color:
        return unpygamize_color(self.__border_color__)
    @border_color.setter
    def border_color(self, new_color:Color|pg.Color) -> None:
        self.__border_color__ = pygamize_color(new_color)

    def draw(self) -> None:
        if self.hidden: return
        self.text_surface.fill(TRANSPARENT_COLOR_PYG)
        
        if self.__bg_color__ is not None:
            pg.draw.rect(self.text_surface, self.__bg_color__(), self.bg_rect, 0, -1, *self.border_radius)
        
        self.text_surface.blit(self.text_box, self.text_position())
        
        if self.rootEnv.selected_util != self:
            if self.border_width:
                pg.draw.rect(self.text_surface, self.__border_color__(), self.margin_rect, self.border_width, -1, *self.border_radius)
        else:
            k = 127.5 + 127.5 * _mt.sin(self.rootEnv.runtime_seconds * 10)
            pg.draw.rect(self.text_surface, pg.Color(k, k, k), self.margin_rect, self.border_width if self.border_width else 10, -1, *self.border_radius)

        self.surface.blit(self.text_surface, self.position())
        
    def update(self) -> None:
        if self.hidden: return
        self.is_hovered = self.position.x < self.rootEnv.mouse.position.x < self.position.x + self.size.x and\
                          self.position.y < self.rootEnv.mouse.position.y < self.position.y + self.size.y
        
        if self.rootEnv.mouse.get_key(0, "just_pressed"):
            if self.is_hovered:
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
            if self.rootEnv.keyboard.get_key(pg.K_RETURN, "just_pressed"):
                self.on_enter_pressed(self.value)
            if self.rootEnv.keyboard.get_key(pg.K_ESCAPE, "just_pressed"):
                self.rootEnv.selected_util = self if self.rootEnv.selected_util != self else None
            self.update_text()

    def update_text(self) -> None:
        self.text_box = self.font.render(self.prefix + self.value, True, self.__text_color__())
        if self.rootEnv != None and self.rootEnv.selected_util == self:
            # self.text_position = self.position + self.size * Vector2D(.85, .5) - Vector2D(*self.text_box.get_size()) * Vector2D(1, .5) - self.position
            self.text_position = self.position + self.size * .5 - Vector2D(*self.text_box.get_size()) * Vector2D(.5, .5) - self.position
        else:
            self.text_position = self.position + self.size * .5 - Vector2D(*self.text_box.get_size()) * Vector2D(.5, .5) - self.position

class Slider(Util):
    def __init__(self,
                text : str,
                position : Vector2D,
                size : Vector2D,
                min_value : float = 0,
                max_value : float = 100,
                step : float = 1,
                color : Color|pg.Color = Color(200, 200, 200),
                handleColour : Color|pg.Color = Color.white(),
                initial_value : float = 0,
                rounded : bool = True,
                handleRadius : float = 10,
                text_offset : V2 = V2(1.1, .5),
                text_pivot : __LITERAL_PIVOT_POSITIONS__ = "center_center",
                personalized_surface : pg.Surface|None = None,
                ) -> None:
        super().__init__()
        
        self.text = text
        self.selected = False
        self.min = min_value
        self.max = max_value
        self.step = step

        self.position = position
        self.size = size

        self.value = clamp(initial_value, self.min, self.max)

        self.radius = self.size.y // 2 if rounded else 0
        self.text_offset = text_offset
        self.text_pivot = text_pivot

        self.handleRadius = handleRadius
        self.surface = personalized_surface

        self.hidden = False

        self.color = color
        self.handleColour = handleColour
    
    @property
    def color(self) -> Color:
        return unpygamize_color(self.__color__)
    @color.setter
    def color(self, new_color:Color|pg.Color) -> None:
        self.__color__ = pygamize_color(new_color)
    @property
    def handleColour(self) -> Color:
        return unpygamize_color(self.__handleColour__)
    @handleColour.setter
    def handleColour(self, new_color:Color|pg.Color) -> None:
        self.__handleColour__ = pygamize_color(new_color)

    def draw(self) -> None:
        if self.hidden: return
        pg.draw.rect(self.rootEnv.screen, self.__color__, self.position() + self.size())

        if self.radius:
            pg.draw.circle(self.rootEnv.screen, self.__color__, (self.position.x, self.position.y + self.size.y // 2), self.radius)
            pg.draw.circle(self.rootEnv.screen, self.__color__, (self.position.x + self.size.x, self.position.y + self.size.y // 2), self.radius)

        circle = V2(int(self.position.x + (self.value - self.min) / (self.max - self.min) * self.size.x), self.position.y + self.size.y // 2)

        pg.draw.circle(self.rootEnv.screen, self.__color__, circle(), self.handleRadius * 1.25)
        pg.draw.circle(self.rootEnv.screen, self.__handleColour__, circle(), self.handleRadius)
        self.rootEnv.print(self.text.format(round(self.value, 2)), self.position + self.size * self.text_offset, pivot_position=self.text_pivot)
    
    def update(self) -> None:
        if self.hidden: return
        x,y = self.rootEnv.mouse.position

        if self.rootEnv.mouse.get_key(0, "just_pressed") and self.__contains__(x, y):
            self.rootEnv.selected_util = self
        elif self.rootEnv.mouse.get_key(0, "just_released"):
            self.rootEnv.selected_util = None
        
        if self.rootEnv.selected_util == self:
            new_value = (x - self.position.x) / self.size.x * self.max + self.min
            self.value = clamp(new_value, self.min, self.max)

    def __contains__(self, x, y) -> bool:
        handleX = self.position.x + (self.value - self.min) / (self.max - self.min) * self.size.x
        handleY = self.position.y + self.size.y // 2
        return (handleX - x) ** 2 + (handleY - y) ** 2 <= self.handleRadius ** 2

    def setValue(self, value) -> None:
        self.value = clamp(value, self.min, self.max)

    def getValue(self) -> float:
        return self.value

class Button(Util):
    def __init__(self,
                text : str,
                position : V2|Vector2D,
                size : V2|Vector2D,
                callback : Callable[[...], None]|Callable[[], None],
                default_color : Color|pg.Color,
                hovered_color : Color|pg.Color,
                border_color : Color|pg.Color,
                text_color : Color|pg.Color = WHITE_COLOR_PYG,
                font : pg.font.Font = FONT_ARIAL_32,
                border_radius : float = 10,
                border_width : float = 10,
                starting_hiddden : bool = False,
                args : list = [],
                activation_mode : __LITERAL_KEY_MODE_TYPES__ = "just_pressed",
                pivot_position : __LITERAL_PIVOT_POSITIONS__ = "top_left",
                personalized_surface : pg.Surface|None = None,
            ) -> None:
        super().__init__()
        
        self.text = text
        self.font = font

        self.callback = callback
        
        self.border_radius = border_radius
        self.__size__ = size
        self.__border_width__ = border_width
        
        self.update_position(position, pivot_position)

        self.hidden = starting_hiddden
        self.args = args

        self.activation_mode = activation_mode
    
        self.hovered = False

        self.text_color = text_color
        self.default_color = default_color
        self.border_color = border_color
        self.hovered_color = hovered_color

        self.surface = personalized_surface
        self.update_surface()
    
    def update_position(self, new_position:V2, pivot_position:__LITERAL_PIVOT_POSITIONS__="top_left") -> None:
        self.position = new_position - (self.__size__ + self.border_width * 2) * __PIVOT_POSITIONS_MULTIPLIER__[pivot_position]
    
    def update_surface(self, render=False) -> None:
        self.buffer_surface = pg.Surface((self.__size__ + self.__border_width__ * 2)(), pg.SRCALPHA, 32).convert_alpha()
        if render: self.render()

    @property
    def size(self) -> V2:
        return self.__size__
    @size.setter
    def size(self, new_size:V2|Vector2D) -> None:
        self.__size__ = new_size
        self.update_surface(render=True)

    @property
    def border_width(self) -> float:
        return self.__border_width__
    @border_width.setter
    def border_width(self, new_width:float) -> None:
        self.__border_width__ = new_width
        self.update_surface(render=True)
    
    @property
    def text_color(self) -> Color:
        return unpygamize_color(self.__text_color__)
    @text_color.setter
    def text_color(self, new_color:Color|pg.Color) -> None:
        self.__text_color__ = pygamize_color(new_color)
    @property
    def default_color(self) -> Color:
        return unpygamize_color(self.__default_color__)
    @default_color.setter
    def default_color(self, new_color:Color|pg.Color) -> None:
        self.__default_color__ = pygamize_color(new_color)
    @property
    def border_color(self) -> Color:
        return unpygamize_color(self.__border_color__)
    @border_color.setter
    def border_color(self, new_color:Color|pg.Color) -> None:
        self.__border_color__ = pygamize_color(new_color)
    @property
    def hovered_color(self) -> Color:
        return unpygamize_color(self.__hovered_color__)
    @hovered_color.setter
    def hovered_color(self, new_color:Color|pg.Color) -> None:
        self.__hovered_color__ = pygamize_color(new_color)

    def render(self) -> None:
        print("rendering button")
        self.buffer_surface.fill(TRANSPARENT_COLOR_PYG)

        color = self.__hovered_color__ if self.hovered else self.__default_color__
        pg.draw.rect(self.buffer_surface, self.__border_color__, V2.zero()() + (self.size + self.border_width * 2)(), border_radius=self.border_radius)
        pg.draw.rect(self.buffer_surface, color, (V2.zero() + self.border_width)() + self.size(), border_radius=self.border_radius)

        self.rootEnv.print(self.text, self.border_width + self.size * .5, color=self.__text_color__, font=self.font, pivot_position="center_center", personalized_surface=self.buffer_surface)

    def draw(self) -> None:
        if self.hidden: return
        self.surface.blit(self.buffer_surface, (self.position)())

    def update(self) -> None:
        if self.hidden: return

        old_overed = self.hovered
        self.hovered = \
            self.position.x < self.rootEnv.mouse.position.x < self.position.x + self.size.x and \
            self.position.y < self.rootEnv.mouse.position.y < self.position.y + self.size.y
        if self.hovered != old_overed:
            self.render()
        
        if self.hovered and self.rootEnv.mouse.get_key(0, self.activation_mode):
            self.callback(*self.args)
            self.rootEnv.selected_util = self
            self.render()
        elif self.rootEnv.selected_util == self:
            self.rootEnv.selected_util = None
            self.render()

class Label(Util):
    def __init__(self,
                text : str,
                position : V2|Vector2D,
                size : V2|Vector2D,
                default_color : Color|pg.Color = TRANSPARENT_COLOR_PYG,
                border_color : Color|pg.Color = WHITE_COLOR_PYG,
                text_color : Color|pg.Color = WHITE_COLOR_PYG,
                font : pg.font.Font = FONT_ARIAL_32,
                border_radius : float = 10,
                border_width : float = 10,
                starting_hiddden : bool = False,
                personalized_surface : pg.Surface|None = None,
                pivot_position : __LITERAL_PIVOT_POSITIONS__ = "top_left",
            ) -> None:
        super().__init__()
        
        self.__text__ = text
        self.font = font

        self.border_radius = border_radius
        self.__size__ = size
        self.__border_width__ = border_width
        
        self.position = self.update_position(position, pivot_position)

        self.hidden = starting_hiddden

        self.text_color = text_color
        self.default_color = default_color
        self.border_color = border_color

        self.surface = personalized_surface
        self.update_surface()
    
    def update_position(self, new_position:V2, pivot_position:__LITERAL_PIVOT_POSITIONS__="top_left") -> None:
        self.position = new_position - (self.__size__ + self.border_width * 2) * __PIVOT_POSITIONS_MULTIPLIER__[pivot_position]
    
    def update_surface(self, render=False) -> None:
        self.buffer_surface = pg.Surface((self.__size__ + self.__border_width__ * 2)(), pg.SRCALPHA, 32).convert_alpha()
        if render: self.render()

    @property
    def text(self) -> str:
        return self.__text__
    @text.setter
    def text(self, new_text:str) -> None:
        self.__text__ = new_text
        self.render()

    @property
    def size(self) -> V2:
        return self.__size__
    @size.setter
    def size(self, new_size:V2|Vector2D) -> None:
        self.__size__ = new_size
        self.update_surface(render=True)

    @property
    def border_width(self) -> float:
        return self.__border_width__
    @border_width.setter
    def border_width(self, new_width:float) -> None:
        self.__border_width__ = new_width
        self.update_surface(render=True)
    
    @property
    def text_color(self) -> Color:
        return unpygamize_color(self.__text_color__)
    @text_color.setter
    def text_color(self, new_color:Color|pg.Color) -> None:
        self.__text_color__ = pygamize_color(new_color)
    @property
    def default_color(self) -> Color:
        return unpygamize_color(self.__default_color__)
    @default_color.setter
    def default_color(self, new_color:Color|pg.Color) -> None:
        self.__default_color__ = pygamize_color(new_color)
    @property
    def border_color(self) -> Color:
        return unpygamize_color(self.__border_color__)
    @border_color.setter
    def border_color(self, new_color:Color|pg.Color) -> None:
        self.__border_color__ = pygamize_color(new_color)

    def render(self) -> None:
        print("rendering label")
        self.buffer_surface.fill(TRANSPARENT_COLOR_PYG)

        pg.draw.rect(self.buffer_surface, self.__border_color__, V2.zero()() + (self.size + self.border_width * 2)(), border_radius=self.border_radius)
        pg.draw.rect(self.buffer_surface, self.__default_color__, (V2.zero() + self.border_width)() + self.size(), border_radius=self.border_radius)

        self.rootEnv.print(self.text, self.border_width + self.size * .5, color=self.__text_color__, font=self.font, pivot_position="center_center", personalized_surface=self.buffer_surface)

    def draw(self) -> None:
        if self.hidden: return
        self.surface.blit(self.buffer_surface, (self.position)())