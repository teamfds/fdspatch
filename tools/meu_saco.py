#!/usr/bin/env python3
from dataclasses import dataclass
import os
import re
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
import tools
from tools import util

tools.load_env_file()

MOD_ROOT = Path(__file__).parent.parent.resolve()
GAME_PATH = os.getenv("GAME_PATH")

class Loc:
    __loc_dir: str = "res/RED/Content/Localization/INT"
    __loc_file: str = f"{__loc_dir}/REDGame.loc"
    move_loc_file: str = f"{__loc_dir}/moves.loc.json"
    __move_loc_map: dict[str, str] = {}
    @staticmethod
    def parse():
        bms_loc_file: str = Loc.__loc_file.replace(".loc", ".uexp")
        if Path(bms_loc_file := Loc.__loc_file.replace(".loc", ".uexp")).exists():
            tools.bbspack(["extract", bms_loc_file, Loc.__loc_file])
            os.remove(bms_loc_file)
        
        with (
            open(Loc.__loc_file, "r", encoding="utf-16") as loc,
            open(Loc.move_loc_file, "w", encoding="utf-16") as move_loc,
        ):
            loc_it = iter(loc)
            first_move = True
            move_loc.write("{\n")
            for line in loc_it:
                if line.startswith("CMCR_"):
                    if not first_move:
                        move_loc.write(",\n")
                        
                    move_cmcr = util.rgx_search_nn(r"CMCR_(\w+)", line, 1)
                    move_name = re.sub(r"(\^m((Atk)|(Btn)))|;", "", next(loc_it).strip())
                    while move_name.find("(Hold)") != -1:
                        move_name = re.sub(r"(.+\s*)\(Hold\)", lambda m: f"[{m.group(1).strip()}]", move_name)
                    move_name = move_name.replace('"', '\\"')
                    
                    move_loc.write(f'  "{move_cmcr}": "{move_name}"')
                    Loc.__move_loc_map[move_cmcr] = move_name
                    
                    first_move = False
            move_loc.write("\n}")
            
    @staticmethod
    def move_loc_get(key: str):
        if key in Loc.__move_loc_map:
            return Loc.__move_loc_map[key]
        # Try normalized search
        key_norm = key.replace("_", "").lower()
        for id, name in Loc.__move_loc_map.items():
            if key_norm in id.replace("_", "").lower():
                return name
        return None
        
    @staticmethod
    def bms_filter():
        return "{}/Localization/INT/REDGame.uexp"
        
class Move:
    @dataclass
    class Token:
        to: str
        prefix: bool = False
        force_name: str | None = None
        
    token_dict: dict[str, Token] = {
        "ANY_FORWARD": Token(to="6", prefix=True),
        "ANY_DOWN": Token(to="2", prefix=True),
        "ANY_DOWNDOWN": Token(to= "22", prefix=True),
        "ANY_BACK": Token(to= "4", prefix=True),
        "CHAR_STATE_JUMPING": Token(to="j.", prefix=True),
        "CLOSE_SLASH": Token(to="c.", prefix=True),
        "FAR_SLASH": Token(to="f.", prefix=True),
        "HOMING_JUMP": Token(to="j"),
        "THROW": Token(to="6D || 4D", force_name="Ground Throw"),
        "AIR_THROW": Token(to="j.6D || j.4D", force_name="Air Throw"),
        "BOOLEAN_OR": Token(to= " || "),
        "DASH": Token(to="🏃‍➡️"),
        "HOLD_DASH": Token(to= "[66]"),
        "HOLD_P": Token(to= "[P]"),
        "HOLD_K": Token(to= "[K]"),
        "HOLD_S": Token(to= "[S]"),
        "HOLD_H": Token(to= "[H]"),
        "HOLD_D": Token(to= "[D]"),
        "TAUNT": Token(to= "Taunt"),
        "DISALLOW_UP": Token(to= ""),
        "NOT_1": Token(to= ""),
        "NOT_3": Token(to= ""),
        "ANY_UP": Token(to= ""),
        
        # ID Tokens
        "HomingJump": Token(to="j"),
        "NmlAtkThrow": Token(to="6D || 4D", force_name="Throw"),
        "NmlAtkAirThrow": Token(to="j.6D || j.4D", force_name="Air Throw"),
        "BKN_SpecialCancel_FDash": Token(to= "", force_name="Parry Dash Cancel"),
        "DustFinish": Token(to="X>X"),
        "WildAssault": Token(to="236D")
    }
    
    def __init__(self, line: str):
        if line == "":
            return
        self.id: str = util.rgx_search_nn(r"s32'(.+?)'", line, 1)
        self.name: str | None = (Loc.move_loc_get(self.id) if self.id.find("NmlAtk") == -1 else None)
        self.input: list[str] = []
        self.sprite: str = ""
        self.char_state: str = ""
        self.flags: list[str] = []
        self.is_move: bool = True
        self.flags.append(self.id)
        
    def parse_char_state(self, line: str):
        self.flags.append(f"CHAR_STATE_{util.rgx_search_nn(r".+?characterState:.+?(\w+)", line, 1)}")
    def parse_input(self, line: str):
        input = util.rgx_search_nn(r".+?moveInput:.+?(\w+)", line, 1)
        self.input.append(re.sub("INPUT_(PRESS_)?", "", input))
    def parse_flag(self, line: str):
        self.flags.append(util.rgx_search_nn(r".+?addMoveFlag:.+?(\w+)", line, 1))
    def parse_sprite(self, line: str):
        if self.sprite != "":
            return
        self.sprite = util.rgx_search_nn(r"s32'(.+?)'", line, 1)
    def render(self):
        if "DEBUG_EX" in self.flags:
            return None
        
        input: list[str] = []
        force_name: str | None = None
        
        for x in self.input:
            if x in Move.token_dict:
                if Move.token_dict[x].prefix:
                    input.insert(0, Move.token_dict[x].to)
                else:
                    input.append(Move.token_dict[x].to)
            else:
                input.append(x)
        
        for x in self.flags:
            if x in Move.token_dict:
                input.insert(0, Move.token_dict[x].to)
                force_name = Move.token_dict[x].force_name
                    
        
        input = [x for x in (input) if len(x) > 0]
        if len(input) == 1 and len(input[0]) == 1 and not input[0].isnumeric():
            input.insert(0, "5")
            
        rendered_input = "".join(input)
        if force_name: 
            name_display = force_name
        else:
            name_display = self.name if self.name else rendered_input
        
        if len(self.sprite) == 0 or re.match(r"((null)|(keep))", self.sprite):
            return None
        else:
            return f"\"{name_display}( {self.id} )\": {{ \"input\": \"{rendered_input}\", \"sprite\": \"{self.sprite}\" }}"
    
    @staticmethod
    def generate_move_list(bbs_path: str):
        moves: dict[str, Move] = {}
        reading_move = False
        state_name = ""
        reading_state = False
        with open(bbs_path) as file:
            current_move = Move("")
            for line in file:
                if line.find("addMove:") != -1:
                    reading_move = True
                    current_move = Move(line)
                elif line.find("endMove:") != -1 and reading_move:
                    reading_move = False
                    if current_move.id not in moves:
                        moves[current_move.id] = current_move
                if reading_move:
                    if line.find("characterState:") != -1:
                        current_move.parse_char_state(line)
                    if line.find("moveInput:") != -1:
                        current_move.parse_input(line)
                    if line.find("addMoveFlag:") != -1:
                        current_move.parse_flag(line)
                        
                if line.find("registerMove:") != -1:
                    mv = Move(line)
                    if mv.id not in moves:
                        moves[mv.id] = mv
                        
                if line.find("beginState:") != -1:
                    mv = Move(line)
                    state_name = mv.id
                    if state_name not in moves:
                        mv.is_move = False
                        moves[state_name] = mv
                    reading_state = True
                if reading_state and line.find("sprite:") != -1:
                    moves[state_name].parse_sprite(line)
                if line.find("endState:") != -1 and reading_state:
                    reading_state = False
                    
            if len(moves) == 0:
                return None
            else:
                move_list = sorted(moves.values(), key=lambda mv: mv.is_move, reverse=True)
                rendered_move_list = [f"    {r}" for m in move_list if (r := m.render()) is not None]
                return f"{{\n{",\n".join(sorted(rendered_move_list, key=lambda mv: mv.startswith("(")))}\n}}"
                 
def extract_game_files(filters: list[str]):
    tools.quickbms([
        "-o",
        "-Y",
        *[item for f in filters for item in ("-f", f)],
        "tools/quickbms/ggst.bms",
        f"{GAME_PATH}/pakchunk0-WindowsNoEditor.pak",
        f"{MOD_ROOT}/res",
    ])
    
def parse_bbs(uexp: str):
    uexp_unpack_dest = uexp.replace(".uexp", ".bbscript")
    uexp_parse_dest = uexp_unpack_dest.replace(".bbscript", ".txt")
    print(f"> Extracting to: {uexp_unpack_dest}")
    print(f"> Parsing to:   {uexp_parse_dest}")
    
    # Extract and parse bbscript
    tools.bbspack(["extract", uexp, uexp_unpack_dest])
    tools.bbscript([
        "parse",
        "--overwrite",
        "--game",
        "ggst",
        uexp_unpack_dest,
        uexp_parse_dest,
    ])
    os.remove(uexp_unpack_dest)
    return uexp_parse_dest
    
def parse_col(uexp: str):
    col_unpack_dest = uexp.replace(".uexp", ".pac")
    print(f"> Extracting to: {col_unpack_dest}")
    # Extract colision file
    tools.bbspack(["extract", uexp, col_unpack_dest])
    return col_unpack_dest
    
def main():
    if GAME_PATH is None:
        print("Missing GAME_PATH environment variable")
        sys.exit()
    os.chdir(MOD_ROOT)
    extract_game_files([
        "{}/Chara/{}Data/{}BBS_{}", 
        "{}/Chara/{}Data/{}COL_{}", 
        Loc.bms_filter()
    ])
    Loc.parse()
        
    for root, _, files in os.walk(f"{MOD_ROOT}/res"):
        for file in files:
            if not re.match(r"((BBS)|(COL))_.*\.uexp", file):
                continue
            uexp = os.path.join(root, file)
            dest = ""
            print(f"Processing: {uexp}")
            if file.startswith("BBS"):
                dest = parse_bbs(uexp)
            elif file.startswith("COL"):
                dest = parse_col(uexp)
            # If is from older patch
            if re.match(r"((BBS)|(COL))_.+_\d+\..+", file):
                print("> Removing old patch assets:")
                print(f">  uexp:   {uexp}")
                print(f">  uasset: {uexp.replace('.uexp', '.uasset')}")
                os.remove(uexp)
                os.remove(uexp.replace(".uexp", ".uasset"))
                print("> Removing patch number from the processed file's name")
                os.rename(dest, re.sub(r"_\d+\.", ".", dest))
            else:
                if re.match(r"BBS_(.{3})\.uexp", file):
                    print(f"> Generating movelist.json for {file.removesuffix('.uexp')}")
                    if move_list := Move.generate_move_list(dest):
                        with open(f"{root}/movelist.json", "w", encoding="utf-8") as move_list_f:
                            move_list_f.write(move_list)
                print("> Moving processed file from current patch into /current directory")
                os.makedirs(f"{root}/current", exist_ok=True)
                os.replace(dest, f"{root}/current/{os.path.basename(dest)}")
main()