#!/usr/bin/env python3
import shutil
import os
from glob import glob
from pathlib import Path
import tools
import sys

tools.load_env_file()

mod_name = "FDSPatch"
mod_root = Path(__file__).parent.resolve()
mod_build_root = f"{mod_root}/build/{mod_name}"
mod_build_content = f"{mod_build_root}/RED/Content"
mod_res_content = f"{mod_root}/res/RED/Content"
mod_src = f"{mod_root}/src"

script_files = [y for x in os.walk(mod_src) for y in glob(os.path.join(x[0], 'BBS_*.txt'))]
pac_files = [y for x in os.walk(mod_src) for y in glob(os.path.join(x[0], '*.pac'))]

install_flag = sys.argv[1] if len(sys.argv) > 1 else ""
os.chdir(mod_root)

os.makedirs(mod_build_content, exist_ok=True)

def abort(e: RuntimeError):
    print(e)
    print("\033[31mAborting build\033[0m")
    sys.exit()
    
def ensure_assets(files: list[str], ext: str):
    for f in files:
        f_build = f.replace(mod_src, mod_build_content)
        uasset_dest = f_build.replace(f".{ext}", ".uasset")
        uexp_dest = f_build.replace(f".{ext}", ".uexp")
        
        res_uasset = f.replace(mod_src, mod_res_content).replace(f".{ext}", ".uasset")
        res_uexp = res_uasset.replace(".uasset", ".uexp")
        
        os.makedirs(os.path.dirname(uasset_dest), exist_ok=True)
        shutil.copy(res_uasset, uasset_dest)
        shutil.copy(res_uexp, uexp_dest)

ensure_assets(pac_files, "pac")
ensure_assets(script_files, "txt")

for script in script_files:
    build_path = script.replace(mod_src, mod_build_content)
    print(f"\033[33m{build_path}\033[0m")
    
    rebuilt_script = build_path.replace(".txt", ".bbscript")
    uasset = build_path.replace(".txt", ".uasset")
    uexp = build_path.replace(".txt", ".uexp")
    
    try:
        tools.bbscript(["rebuild", "--game", "ggst", "--overwrite", script, rebuilt_script])
        tools.bbspack(["inject", rebuilt_script, uexp, uasset])
        os.remove(rebuilt_script)
    except RuntimeError as e:
        abort(e)
        
for pac in pac_files:
    build_path = pac.replace(mod_src, mod_build_content)
    print(f"\033[33m{build_path}\033[0m")
    
    uasset_pac = build_path.replace(".pac", ".uasset")
    uexp_pac = build_path.replace(".pac", ".uexp")
    try:
        tools.bbspack(["inject", pac, uexp_pac, uasset_pac])
    except RuntimeError as e:
        abort(e)

try:
    tools.u4pak(["pack",
        f"build/{mod_name}.pak",
        f":none,rename=/RED:build/{mod_name}/RED",
        "--mount-point=../../..",
        "--version=3"
    ])
except RuntimeError as e:
    abort(e)

shutil.copy("src/pakchunk0-WindowsNoEditor.sig", f"build/{mod_name}.sig")
shutil.rmtree(mod_build_root)

game_path = os.getenv("GAME_PATH")
if install_flag == "-I" and game_path:
    install_path = f"{game_path}/~mods/{mod_name}"
    os.makedirs(install_path, exist_ok=True)
    shutil.copy(f"build/{mod_name}.sig", f"{install_path}/{mod_name}.sig")
    shutil.copy(f"build/{mod_name}.pak", f"{install_path}/{mod_name}.pak")
