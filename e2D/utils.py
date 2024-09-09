from __future__ import annotations
from typing import Any, Callable, Literal
import pygame as pg
from e2D import *

pg.font.init()

__KEY_MODE_TYPES_DICT__ = dict(zip(["pressed", "just_pressed", "just_released"], range(3)))
__LITERAL_KEY_MODE_TYPES__ = Literal["pressed", "just_pressed", "just_released"]

__LITERAL_FONTS__ = Literal['arial', 'arialblack', 'bahnschrift', 'calibri', 'cambria', 'cambriamath', 'candara', 'comicsansms', 'consolas', 'constantia', 'corbel', 'couriernew', 'ebrima', 'franklingothicmedium', 'gabriola', 'gadugi', 'georgia', 'impact', 'inkfree', 'javanesetext', 'leelawadeeui', 'leelawadeeuisemilight', 'lucidaconsole', 'lucidasans', 'malgungothic', 'malgungothicsemilight', 'microsofthimalaya', 'microsoftjhenghei', 'microsoftjhengheiui', 'microsoftnewtailue', 'microsoftphagspa', 'microsoftsansserif', 'microsofttaile', 'microsoftyahei', 'microsoftyaheiui', 'microsoftyibaiti', 'mingliuextb', 'pmingliuextb', 'mingliuhkscsextb', 'mongolianbaiti', 'msgothic', 'msuigothic', 'mspgothic', 'mvboli', 'myanmartext', 'nirmalaui', 'nirmalauisemilight', 'palatinolinotype', 'segoemdl2assets', 'segoeprint', 'segoescript', 'segoeui', 'segoeuiblack', 'segoeuiemoji', 'segoeuihistoric', 'segoeuisemibold', 'segoeuisemilight', 'segoeuisymbol', 'simsun', 'nsimsun', 'simsunextb', 'sitkasmall', 'sitkatext', 'sitkasubheading', 'sitkaheading', 'sitkadisplay', 'sitkabanner', 'sylfaen', 'symbol', 'tahoma', 'timesnewroman', 'trebuchetms', 'verdana', 'webdings', 'wingdings', 'yugothic', 'yugothicuisemibold', 'yugothicui', 'yugothicmedium', 'yugothicuiregular', 'yugothicregular', 'yugothicuisemilight', 'holomdl2assets', 'bizudgothic', 'bizudpgothictruetype', 'bizudminchomedium', 'bizudpminchomediumtruetype', 'meiryo', 'meiryoui', 'msmincho', 'mspmincho', 'uddigikyokashonb', 'uddigikyokashonpb', 'uddigikyokashonkb', 'uddigikyokashonr', 'uddigikyokashonpr', 'uddigikyokashonkr', 'yumincho', 'lcd', 'glassgauge', 'maiandragd', 'maiandragddemi', 'newsgothic', 'quartz', 'kievitoffcpro', 'agencyfbgrassetto', 'agencyfb', 'algerian', 'bookantiquagrassetto', 'bookantiquagrassettocorsivo', 'bookantiquacorsivo', 'arialcorsivo', 'arialrounded', 'baskervilleoldface', 'bauhaus93', 'bell', 'bellgrassetto', 'bellcorsivo', 'bernardcondensed', 'bookantiqua', 'bodonigrassetto', 'bodonigrassettocorsivo', 'bodoniblackcorsivo', 'bodoniblack', 'bodonicondensedgrassetto', 'bodonicondensedgrassettocorsivo', 'bodonicondensedcorsivo', 'bodonicondensed', 'bodonicorsivo', 'bodonipostercompressed', 'bodoni', 'bookmanoldstyle', 'bookmanoldstylegrassetto', 'bookmanoldstylegrassettocorsivo', 'bookmanoldstylecorsivo', 'bradleyhanditc', 'britannic', 'berlinsansfbgrassetto', 'berlinsansfbdemigrassetto', 'berlinsansfb', 'broadway', 'brushscriptcorsivo', 'bookshelfsymbol7', 'californianfbgrassetto', 'californianfbcorsivo', 'californianfb', 'calisto', 'calistograssetto', 'calistograssettocorsivo', 'calistocorsivo', 'castellar', 'centuryschoolbook', 'centaur', 'century', 'chiller', 'colonna', 'cooperblack', 'copperplategothic', 'curlz', 'dubai', 'dubaimedium', 'dubairegular', 'elephant', 'elephantcorsivo', 'engravers', 'erasitc', 'erasdemiitc', 'erasmediumitc', 'felixtitling', 'forte', 'franklingothicbook', 'franklingothicbookcorsivo', 'franklingothicdemi', 'franklingothicdemicond', 'franklingothicdemicorsivo', 'franklingothicheavy', 'franklingothicheavycorsivo', 'franklingothicmediumcond', 'freestylescript', 'frenchscript', 'footlight', 'garamond', 'garamondgrassetto', 'garamondcorsivo', 'gigi', 'gillsansgrassettocorsivo', 'gillsansgrassetto', 'gillsanscondensed', 'gillsanscorsivo', 'gillsansultracondensed', 'gillsansultra', 'gillsans', 'gloucesterextracondensed', 'gillsansextcondensed', 'centurygothic', 'centurygothicgrassetto', 'centurygothicgrassettocorsivo', 'centurygothiccorsivo', 'goudyoldstyle', 'goudyoldstylegrassetto', 'goudyoldstylecorsivo', 'goudystout', 'harlowsolid', 'harrington', 'haettenschweiler', 'hightowertext', 'hightowertextcorsivo', 'imprintshadow', 'informalroman', 'blackadderitc', 'kristenitc', 'jokerman', 'juiceitc', 'kunstlerscript', 'widelatin', 'lucidabright', 'lucidacalligraphy', 'leelawadee', 'leelawadeegrassetto', 'lucidafax', 'lucidafaxdemigrassetto', 'lucidafaxdemigrassettocorsivo', 'lucidafaxcorsivo', 'lucidahandwritingcorsivo', 'lucidasansdemigrassetto', 'lucidasansdemigrassettocorsivo', 'lucidasanscorsivo', 'lucidasanstypewriter', 'lucidasanstypewritergrassetto', 'lucidasanstypewritergrassettooblique', 'lucidasanstypewriteroblique', 'magnetograssetto', 'maturascriptcapitals', 'mistral', 'modernno20', 'microsoftuighurgrassetto', 'microsoftuighur', 'monotypecorsiva', 'extra', 'niagaraengraved', 'niagarasolid', 'ocraextended', 'oldenglishtext', 'onyx', 'msoutlook', 'palacescript', 'papyrus', 'parchment', 'perpetuagrassettocorsivo', 'perpetuagrassetto', 'perpetuacorsivo', 'perpetuatitlinggrassetto', 'perpetuatitlingchiarissimo', 'perpetua', 'playbill', 'poorrichard', 'pristina', 'rage', 'ravie', 'msreferencesansserif', 'msreferencespecialty', 'rockwellcondensedgrassetto', 'rockwellcondensed', 'rockwell', 'rockwellgrassetto', 'rockwellgrassettocorsivo', 'rockwellextra', 'rockwellcorsivo', 'centuryschoolbookgrassetto', 'centuryschoolbookgrassettocorsivo', 'centuryschoolbookcorsivo', 'script', 'showcardgothic', 'snapitc', 'stencil', 'twcengrassettocorsivo', 'twcengrassetto', 'twcencondensedgrassetto', 'twcencondensedextra', 'twcencondensed', 'twcencorsivo', 'twcen', 'tempussansitc', 'vinerhanditc', 'vivaldicorsivo', 'vladimirscript', 'wingdings2', 'wingdings3', 'cascadiacoderegular', 'cascadiamonoregular', 'edwardianscriptitcnormale', 'stoneharbourregular', 'mregular', 'xirodregular', 'minecraft']

NEW_FONT :Callable[[int, __LITERAL_FONTS__, bool, bool], pg.font.Font]= lambda size, name="arial", bold=False, italic=False: pg.font.SysFont(name, size, bold, italic)
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
        self.__pressed__ :list= pg.key.get_pressed()
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
        self.surface : pg.Surface
        self.id : int|str
    def draw(self) -> None: pass
    def update(self) -> None: pass

class InputCell(Util):
    def __init__(self,
                id : int|str,
                initial_value : str,
                position : Vector2D,
                size : Vector2D,
                prefix : str|None = None,
                text_color : tuple[int,int,int]|list[int] = (255,255,255),
                bg_color : None|tuple[int,int,int]|list[int] = None,
                border_color : None|tuple[int,int,int]|list[int] = (255,255,255),
                border_width : float = 0,
                border_radius : int|list[int]|tuple[int,int,int,int] = -1,
                margin : Vector2D = Vector2D.zero(),
                pivot_position : __LITERAL_PIVOT_POSITIONS__ = "center_center",
                font : pg.font.Font = FONT_ARIAL_32,
                personalized_surface : pg.Surface|None = None,
                on_enter_pressed : Callable[[str], Any] = lambda full_text: ...,
                check_when_adding : Callable[[str], str] = lambda new_text: new_text
                ) -> None:
        super().__init__()

        self.id = id
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
        if self.rootEnv.mouse.get_key(0, "just_pressed"):
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
            if self.rootEnv.keyboard.get_key(pg.K_RETURN, "just_pressed"):
                self.on_enter_pressed(self.value)
            if self.rootEnv.keyboard.get_key(pg.K_ESCAPE, "just_pressed"):
                self.rootEnv.selected_util = self if self.rootEnv.selected_util != self else None
            self.update_text()

    def update_text(self) -> None:
        self.text_box = self.font.render(self.prefix + self.value, True, self.text_color)
        if self.rootEnv != None and self.rootEnv.selected_util == self:
            # self.text_position = self.position + self.size * Vector2D(.85, .5) - Vector2D(*self.text_box.get_size()) * Vector2D(1, .5) - self.position
            self.text_position = self.position + self.size * .5 - Vector2D(*self.text_box.get_size()) * Vector2D(.5, .5) - self.position
        else:
            self.text_position = self.position + self.size * .5 - Vector2D(*self.text_box.get_size()) * Vector2D(.5, .5) - self.position
