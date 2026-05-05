import shutil
import os
import subprocess
from glob import glob
from pathlib import Path
from sys import platform

mod_name = "FDSPatch"
mod_root = Path(__file__).parent.resolve()
mod_build_root = f"build/{mod_name}"
mod_build_content = f"{mod_build_root}/RED/Content"

res_files = [y for x in os.walk(f"{mod_root}/res/Content") for y in glob(os.path.join(x[0], 'BBS_*'))]
src_files = [y for x in os.walk(f"{mod_root}/src") for y in glob(os.path.join(x[0], 'BBS_*'))]

os.chdir(mod_root)

os.makedirs(mod_build_content, exist_ok=True)

for file in res_files:
    dest = file.replace("res/Content", mod_build_content)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy(file, dest)

for file in src_files:
    uasset = file.replace("src", mod_build_content).replace(".txt", ".uasset")
    uexp = file.replace("src", mod_build_content).replace(".txt", ".uexp")
    subprocess.run(["tools/bbs_unpacker/target/debug/ggst-bbs-unpacker", "inject", file, uexp, uasset])


if platform == 'linux':
    subprocess.run(["tools/u4pak/u4pak", "pack", f"build/{mod_name}.pak", f"build/{mod_name}"])
elif platform == 'win32':
    subprocess.run(["tools/u4pak/u4pak.exe", "pack", f"build/{mod_name}.pak", f"build/{mod_name}"])
else:
    print("Se mata negao")
    
shutil.copy("res/Content/pakchunk0-WindowsNoEditor.sig", f"build/{mod_name}.sig")
shutil.rmtree(mod_build_root)