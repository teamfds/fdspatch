#!/usr/bin/env python3
import sys
import os
from pathlib import Path
import shutil
sys.path.append(str(Path(__file__).parent.parent))
import tools

mod_root = Path(__file__).parent.resolve()
os.chdir(mod_root)


if len(sys.argv) < 4:
    print("Usage: python3 fix_version.py <path_to_broken_version_no_ext> <path_to_current_patch_version_no_ext> <out_dir>")
    print("  Ex: python3 fix_version.py ./BBS_TST_407 ./BBS_TST build/fixed")
    sys.exit(1)

broken_version = os.path.basename(sys.argv[1])
broken_version_txt = sys.argv[1]
broken_version_uasset = f"{sys.argv[1]}.uasset"
broken_version_uexp = f"{sys.argv[1]}.uexp"

current_version = os.path.basename(sys.argv[2])
current_version_uasset = f"{sys.argv[2]}.uasset"
current_version_uexp =  f"{sys.argv[2]}.uexp"


out_dir = sys.argv[3]

os.makedirs(out_dir, exist_ok=True)

shutil.copy(current_version_uasset, out_dir)
shutil.copy(current_version_uexp, out_dir)

print(broken_version)
if broken_version.endswith(".txt"):
    rebuilt_file = f"{out_dir}/{broken_version}".replace(".txt", ".bbscript")
    tools.bbscript(["rebuild", "--game", "ggst", "--overwrite", broken_version_txt, rebuilt_file])
    tools.bbspack(["inject", rebuilt_file, f"{out_dir}/{current_version}.uexp", f"{out_dir}/{current_version}.uasset"])

    os.remove(rebuilt_file)
else:
    unpack_dest = f"{out_dir}/{broken_version}.bbscript"

    tools.bbspack(["extract", broken_version_uexp, unpack_dest])
    tools.bbspack(["inject", unpack_dest, f"{out_dir}/{current_version}.uexp", f"{out_dir}/{current_version}.uasset"])

    os.remove(unpack_dest)
