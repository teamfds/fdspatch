#!/usr/bin/env python3
import subprocess
from pathlib import Path
import os

mod_root = Path(__file__).parent.resolve()
os.chdir(mod_root)

env = os.environ.copy()

# 2. Adiciona ou sobrescreve o RUSTFLAGS
env["RUSTFLAGS"] = "-A warnings"

if len(os.listdir("tools/bbscript")) == 0:
    subprocess.run(["git", "submodule", "update", "--init", "--recursive"])
else:
    subprocess.run(["git", "submodule", "update", "--remote", "--recursive"])
# BBSPack
subprocess.run(["cargo", "build", "--release", "--manifest-path", "tools/bbspack/Cargo.toml"], env=env, check=True)
# BBScript
subprocess.run(["cargo", "build", "--release", "--manifest-path", "tools/bbscript/Cargo.toml"], env=env, check=True)
# U4Pak
subprocess.run(["cargo", "build", "--release", "--manifest-path", "tools/u4pak/Cargo.toml"], env=env, check=True)
