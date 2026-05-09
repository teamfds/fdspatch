#!/usr/bin/env python3
import os
from pathlib import Path
import sys
import re
from typing import cast

sys.path.append(str(Path(__file__).parent.parent))
import tools

tools.load_env_file()

mod_root = Path(__file__).parent.parent.resolve()
os.chdir(mod_root)

class Move:
    def __init__(self, line: str):
        if line == "": 
            return
        self.id: str = cast(re.Match[str], re.search(r"s32'(.+?)'", line)).group(1)
        self.name: str | None = Move.get_real_name(self.id) if self.id.find("NmlAtk") == -1 else None
        self.input: list[str] = []
        self.sprite: str = ""
        self.char_state: str = ""
        self.flags: list[str] = []
        
    def parse_char_state(self, line: str):
        self.char_state = cast(re.Match[str], re.search(r".+?characterState:.+?(\w+)", line)).group(1)
    def parse_input(self, line: str):
        input = cast(re.Match[str], re.search(r".+?moveInput:.+?(\w+)", line)).group(1)
        self.input.append(re.sub("INPUT_(PRESS_)?", "", input))
    def parse_flag(self, line: str):
        self.flags.append(cast(re.Match[str], re.search(r".+?addMoveFlag:.+?(\w+)", line)).group(1))
    def parse_sprite(self, line: str):
        if self.sprite != "":
            return
        self.sprite = cast(re.Match[str], re.search(r"s32'(.+?)'", line)).group(1)
        
    def render(self):
        if "DEBUG_EX" in self.flags:
            return None
        input_clone: list[str] = self.input
    
        if "DISALLOW_UP" in input_clone:
            input_clone.remove("DISALLOW_UP")
        if "ANY_FORWARD" in input_clone:
            input_clone.remove("ANY_FORWARD")
            input_clone.insert(0, "6")
        if "ANY_DOWN" in input_clone:
            input_clone.remove("ANY_DOWN")
            input_clone.insert(0, "2")
        if "ANY_DOWNDOWN" in input_clone:
            input_clone.remove("ANY_DOWNDOWN")
            input_clone.insert(0, "22")
        if "ANY_BACK" in input_clone:
            input_clone.remove("ANY_BACK")
            input_clone.insert(0, "4")
        if "NOT_1" in input_clone:
            input_clone.remove("NOT_1")
        if "NOT_3" in input_clone:
            input_clone.remove("NOT_3")
        if "ANY_UP" in input_clone:
            input_clone.remove("ANY_UP")
        if "JUMPING" in self.char_state:
            input_clone.insert(0, "j.")
        if "CLOSE_SLASH" in self.flags:
            input_clone.insert(0, "c.")
        if "FAR_SLASH" in self.flags:
            input_clone.insert(0, "f.")
        
        if len(input_clone) == 1 and len(input_clone[0]) == 1 and not input_clone[0].isnumeric():
            input_clone.insert(0, "5")
        if self.id == "HomingJump":
            input_clone.insert(0, "j")
            
        rendered_input = "".join(input_clone)
        
        if self.name:
            return (f"{self.name}( {self.id} ): {{ input: {rendered_input}; sprite: {self.sprite}; }}")
        else:
            return (f"{rendered_input}( {self.id} ): {{ input: {rendered_input}; sprite: {self.sprite}; }}")
    
    @staticmethod
    def get_real_name(id: str):
        with open("res/RED/Content/Localization/POR/REDGame.loc") as loc:
            get_next = False
            for line in loc:
                if get_next:
                    try:
                        return line.strip()
                        # return cast(re.Match[str], re.search(r"(.+) -", line)).group(1).strip()
                    except AttributeError as _:
                        print(f"Error got {line}")
                        return None
                if line.strip() == (f"CMCR_{id}"):
                    get_next = True
            
            return None
            
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
                
                if line.find("beginState:") != -1:
                    state_name = cast(re.Match[str], re.search(r"s32'(.+?)'", line)).group(1)
                    
                    if state_name in moves:
                        reading_state = True
                
                if reading_state and line.find("sprite:") != -1:
                    moves[state_name].parse_sprite(line)
                
                if line.find("endState:") != -1 and reading_state:
                    reading_state = False
            
            if len(moves) == 0:
                return None
            else:
                return "\n".join([r for m in moves.values() if (r := m.render()) is not None])

GAME_PATH = os.getenv("GAME_PATH")

if GAME_PATH is None:
    print("Missing GAME_PATH environment variable")
    sys.exit()
    
tools.quickbms([
    "-o", "-Y", 
    "-f", "{}/Chara/{}Data/{}BBS_{}",
    "-f", "{}/Chara/{}Data/{}COL_{}",
    "tools/quickbms/ggst.bms",
    f"{GAME_PATH}/pakchunk0-WindowsNoEditor.pak",
    f"{mod_root}/res"
])

for root, _, files in os.walk(f"{mod_root}/res"):
    for file in files:
        if not re.match(r'((BBS)|(COL))_.*\.uexp', file):
            continue
        
        uexp = os.path.join(root, file)
        dest = ""
        print(f"Processing: {uexp}")
        
        if file.startswith("BBS"):
            uexp_unpack_dest = uexp.replace(".uexp", ".bbscript")
            uexp_parse_dest = uexp_unpack_dest.replace(".bbscript", ".txt")
            print(f"> Extracting to: {uexp_unpack_dest}")
            print(f"> Parsing to:   {uexp_parse_dest}")
            
            # Extract and parse bbscript
            tools.bbspack(["extract", uexp, uexp_unpack_dest])
            tools.bbscript(["parse", "--overwrite", "--game", "ggst", uexp_unpack_dest, uexp_parse_dest])
            os.remove(uexp_unpack_dest)
            dest = uexp_parse_dest
        elif file.startswith("COL"):
            col_unpack_dest = uexp.replace(".uexp", ".pac")
            print(f"> Extracting to: {col_unpack_dest}")
            # Extract colision file
            tools.bbspack(["extract", uexp, col_unpack_dest])
            dest = col_unpack_dest
            
        # If is from older patch
        if re.match(r"((BBS)|(COL))_.+_\d+\..+", file):
            print("> Removing old patch assets:")
            print(f">  uexp:   {uexp}")
            print(f">  uasset: {uexp.replace(".uexp", ".uasset")}")
            os.remove(uexp)
            os.remove(uexp.replace(".uexp", ".uasset"))
            
            print("> Removing patch number from the processed file's name")
            os.rename(dest, re.sub(r"_\d+\.", ".", dest))
        else:
            if re.match(r"BBS_(.{3})\.uexp", file):
                print(f"> Generating movelist.txt for {file.removesuffix(".uexp")}")
                if move_list := Move.generate_move_list(dest):
                    with open(f"{root}/movelist.txt", "w", encoding="utf-8") as move_list_f:
                        move_list_f.write(move_list)
                    
            print("> Moving processed file from current patch into /current directory")
            os.makedirs(f"{root}/current", exist_ok=True)
            os.replace(dest, f"{root}/current/{os.path.basename(dest)}")