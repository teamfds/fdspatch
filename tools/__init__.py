import subprocess
from pathlib import Path
import sys
import os

tools_root = Path(__file__).parent.resolve()

def bbscript(args: list[str]):
    if sys.platform == 'linux':
        _ = subprocess.run([f"{tools_root}/bbscript/target/release/bbscript", *args])
    elif sys.platform == 'win32':
        _ = subprocess.run([f"{tools_root}/bbscript/target/release/bbscript.exe", *args])
    else:
        print("Se mata negao")

def bbspack(args: list[str]):
    if sys.platform == 'linux':
        _ = subprocess.run([f"{tools_root}/bbspack/target/release/bbspack", *args])
    elif sys.platform == 'win32':
        _ = subprocess.run([f"{tools_root}/bbspack/target/release/bbspack.exe", *args])
    else:
        print("Se mata negao")

def u4pak(args: list[str]):
    if sys.platform == 'linux':
        _ = subprocess.run([f"{tools_root}/u4pak/target/release/u4pak", *args])
    elif sys.platform == 'win32':
        _ = subprocess.run([f"{tools_root}/u4pak/target/release/u4pak.exe", *args])
    else:
        print("Se mata negao")

def fix_version(args: list[str]):
    subprocess.run([sys.executable, f"{tools_root}/fix_version.py", *args])
def load_env_file(filepath: str = ".env"):
    if not os.path.exists(filepath):
        return

    with open(filepath, "r") as f:
        for line in f:
            # Remove espaços e ignora linhas vazias ou comentários
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Divide a linha no primeiro '=' encontrado
            if "=" in line:
                key, value = line.split("=", 1)

                # Remove aspas se existirem (ex: "valor" ou 'valor')
                key = key.strip()
                value = value.strip().strip('"').strip("'")

                # Define a variável no ambiente
                os.environ[key] = value
