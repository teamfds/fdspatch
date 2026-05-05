import os
import subprocess
from glob import glob
from pathlib import Path
import sys

mod_name = "FDSPatch"
mod_root = Path(__file__).parent.resolve()
mod_build_root = f"build/{mod_name}"
mod_build_content = f"{mod_build_root}/RED/Content"

os.chdir(mod_root)

if len(sys.argv) == 1:
    print("Faltou o nome do script aí filho da puta")
    sys.exit(1)
    
bbs_uexp_files = [y for x in os.walk(f"{mod_root}/res/Content") for y in glob(os.path.join(x[0], f"{sys.argv[1]}.uexp"))]

for file in bbs_uexp_files:
    unpack_dest = file.replace("res", "res/parsed_bbs").replace(".uexp", ".bbscript")
    parse_dest = unpack_dest.replace(".bbscript", ".txt")
    
    os.makedirs(os.path.dirname(unpack_dest), exist_ok=True)
    subprocess.run(["tools/bbs_unpacker/target/debug/ggst-bbs-unpacker", 
        "extract", 
        "--overwrite",
        file, 
        unpack_dest, 
    ])
    
    subprocess.run(["tools/bbscript/target/debug/bbscript",
        "parse",
        "--overwrite",
        "--game", "ggst",
        unpack_dest, parse_dest
    ])
    os.remove(unpack_dest)
