#!/usr/bin/env python3
import shutil
import os
from glob import glob
from pathlib import Path
import tools
import sys

# tools.load_env_file()

mod_name = "FDSPatch"
mod_root = Path(__file__).parent.resolve()
mod_build_root = f"build/{mod_name}"
mod_build_content = f"{mod_build_root}/RED/Content"

uasset_files = [y for x in os.walk(f"{mod_root}/src") for y in glob(os.path.join(x[0], '*.uasset'))]
script_files = [y for x in os.walk(f"{mod_root}/src") for y in glob(os.path.join(x[0], 'BBS_*.txt'))]
pac_files = [y for x in os.walk(f"{mod_root}/src") for y in glob(os.path.join(x[0], '*.pac'))]

install_flag = sys.argv[1] if len(sys.argv) > 1 else ""
os.chdir(mod_root)

os.makedirs(mod_build_content, exist_ok=True)

def ensure_assets(files, ext):
    for f in files:
        f_build = f.replace("src", mod_build_content)
        uasset_dest = f_build.replace(f".{ext}", ".uasset")
        res_uasset = f.replace(f"{mod_root}/src", f"{mod_root}/res/RED/Content").replace(f".{ext}", ".uasset")
        res_uexp = res_uasset.replace(".uasset", ".uexp")
        os.makedirs(os.path.dirname(uasset_dest), exist_ok=True)
        shutil.copy(res_uasset, uasset_dest)
        shutil.copy(res_uexp, uasset_dest.replace(".uasset", ".uexp"))

ensure_assets(pac_files, "pac")
ensure_assets(script_files, "txt")

for uasset in uasset_files:
    uasset_dest = uasset.replace("src", mod_build_content)
    uexp = uasset.replace(".uasset", ".uexp")
    uexp_dest = uexp.replace("src", mod_build_content)

    os.makedirs(os.path.dirname(uasset_dest), exist_ok=True)
    shutil.copy(uasset, uasset_dest)
    shutil.copy(uexp, uexp_dest)

for script in script_files:
    rebuilt_file = script.replace("src", mod_build_content).replace(".txt", ".bbscript")
    uasset = script.replace("src", mod_build_content).replace(".txt", ".uasset")
    uexp = script.replace("src", mod_build_content).replace(".txt", ".uexp")

    tools.bbscript(["rebuild", "--game", "ggst", "--overwrite", script, rebuilt_file])
    tools.bbspack(["inject", rebuilt_file, uexp, uasset])
    os.remove(rebuilt_file)

for pac in pac_files:
    uasset_pac = pac.replace("src", mod_build_content).replace(".pac", ".uasset")
    uexp_pac = pac.replace("src", mod_build_content).replace(".pac", ".uexp")
    tools.bbspack(["inject", pac, uexp_pac, uasset_pac])

tools.u4pak(["pack",
    f"build/{mod_name}.pak",
    f":none,rename=/RED:build/{mod_name}/RED",
    "--mount-point=../../..",
    "--version=3"
])

shutil.copy("src/pakchunk0-WindowsNoEditor.sig", f"build/{mod_name}.sig")
shutil.rmtree(mod_build_root)

game_path = os.getenv("GAME_PATH")
if install_flag == "-I" and game_path:
    install_path = f"{game_path}/~mods/{mod_name}"
    os.makedirs(install_path)
    shutil.copy(f"build/{mod_name}.sig", f"{install_path}/{mod_name}.sig")
    shutil.copy(f"build/{mod_name}.pak", f"{install_path}/{mod_name}.pak")
