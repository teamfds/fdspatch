#!/usr/bin/env python3
import os
from pathlib import Path
import sys
import re
import shutil

sys.path.append(str(Path(__file__).parent.parent))
import tools

tools.load_env_file()

mod_root = Path(__file__).parent.parent.resolve()
os.chdir(mod_root)

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

# python3 tools/meu_saco.py
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
            print("> Moving processed file from current patch into /current directory")
            os.makedirs(f"{root}/current", exist_ok=True)
            shutil.move(dest, f"{root}/current")