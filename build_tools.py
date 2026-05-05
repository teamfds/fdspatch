import subprocess
from pathlib import Path
import os

mod_root = Path(__file__).parent.resolve()
os.chdir(mod_root)

# BBS Unpacker
subprocess.run(["cargo", "build", "--no-default-features", "--manifest-path", "tools/bbs_unpacker/Cargo.toml"])
# BBScript
subprocess.run(["cargo", "build", "--manifest-path", "tools/bbscript/Cargo.toml"])