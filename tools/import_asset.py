#!/usr/bin/env python3
import sys
import os
from pathlib import Path
from glob import glob
import re
sys.path.append(str(Path(__file__).parent.parent))
import tools

mod_root = Path(__file__).parent.parent.resolve()
os.chdir(mod_root)

if len(sys.argv) < 2:
    print("Usage: python3 import_asset.py <BBS_FILE_NAME>")
    print("  Ex: python3 import_asset.py BBS_TST_407")
    sys.exit(1)

target = sys.argv[1]
current = re.sub(r'_\d+$', "", target)

target_path = glob(f'{mod_root}/res/**/*{target}.uasset', recursive=True)[0].removesuffix(".uasset")
current_path = glob(f'{mod_root}/res/**/*{current}.uasset', recursive=True)[0].removesuffix(".uasset")
out_dir = os.path.dirname(current_path.replace(f'res/RED/Content', "src"))

tools.fix_version([target_path, current_path, out_dir])
