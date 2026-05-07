import os
from pathlib import Path
import sys
import re


sys.path.append(str(Path(__file__).parent.parent))
import tools

mod_root = Path(__file__).parent.parent.resolve()
os.chdir(mod_root)

script_path = './your_script.py'

for root, dirs, files in os.walk(f"{mod_root}/res"):
    for file in files:
        if re.match(r'BBS_.*\.uexp', file):
            full_path = os.path.join(root, file)
            unpack_dest = full_path.replace(".uexp", ".bbscript")
            parse_dest = unpack_dest.replace(".bbscript", ".txt")

            print(f"Processing: {full_path}")
            print(f"            {unpack_dest}")
            print(f"            {parse_dest}")

            tools.bbspack(["extract", full_path, unpack_dest])
            tools.bbscript(["parse", "--overwrite", "--game", "ggst", unpack_dest, parse_dest])

            os.remove(unpack_dest)

        elif re.match(r'COL_.*\.uexp', file):
            full_path = os.path.join(root, file)
            pac_dest = full_path.replace(".uexp", ".pac")

            print(f"Extracting COL: {full_path}")
            print(f"           -> {pac_dest}")

            tools.bbspack(["extract", full_path, pac_dest])
