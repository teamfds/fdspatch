import sys
import os
import subprocess
from pathlib import Path
import shutil

mod_root = Path(__file__).parent.resolve()
os.chdir(mod_root)


if len(sys.argv) < 4:
    print("Usage: python3 fix_version.py <path_to_broken_version_no_ext> <path_to_current_patch_version_no_ext> <out_dir>")
    print("  Ex: python3 fix_version.py ./BBS_TST_407 ./BBS_TST build/fixed")
    sys.exit(1)
    

broken_version = os.path.basename(sys.argv[1])
broken_version_uasset = f"{sys.argv[1]}.uasset"
broken_version_uexp = f"{sys.argv[1]}.uexp"

current_version = os.path.basename(sys.argv[2])
current_version_uasset = f"{sys.argv[2]}.uasset"
current_version_uexp =  f"{sys.argv[2]}.uexp"


out_dir = sys.argv[3]

os.makedirs(out_dir, exist_ok=True)

shutil.copy(current_version_uasset, out_dir) 
shutil.copy(current_version_uexp, out_dir) 

unpack_dest = f"{out_dir}/{broken_version}.bbscript"
print(broken_version_uexp)
subprocess.run(["tools/bbs_unpacker/target/debug/ggst-bbs-unpacker", 
    "extract", 
    "--overwrite",
    broken_version_uexp, 
    unpack_dest, 
])

subprocess.run(["tools/bbs_unpacker/target/debug/ggst-bbs-unpacker", 
    "inject", 
    unpack_dest, 
    f"{out_dir}/{current_version}.uexp", 
    f"{out_dir}/{current_version}.uasset"
])
os.remove(unpack_dest)
