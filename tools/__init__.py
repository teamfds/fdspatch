import subprocess
from pathlib import Path
import sys
import os

tools_root = Path(__file__).parent.resolve()

def check_result(result: subprocess.CompletedProcess[str]):
    stdout = result.stdout.removesuffix("\n")
    if result.returncode != 0: 
        raise RuntimeError(f"\033[31m{stdout}\033[0m") 
    elif len(result.stdout) > 0:
        print(f"\033[34m{stdout}||\033[0m") 
        
def bbscript(args: list[str]):
    if sys.platform == 'linux':
        result = subprocess.run([f"{tools_root}/bbscript/target/release/bbscript", *args], capture_output=True, text=True)
    elif sys.platform == 'win32':
        result = subprocess.run([f"{tools_root}/bbscript/target/release/bbscript.exe", *args], capture_output=True, text=True)
    else:
        return print("Se mata negao")
        
    check_result(result)
        
def bbspack(args: list[str]):
    if sys.platform == 'linux':
        result = subprocess.run([f"{tools_root}/bbspack/target/release/bbspack", *args], capture_output=True, text=True)
    elif sys.platform == 'win32':
        result = subprocess.run([f"{tools_root}/bbspack/target/release/bbspack.exe", *args], capture_output=True, text=True)
    else:
        return print("Se mata negao")
    
    check_result(result)
        
def u4pak(args: list[str]):
    if sys.platform == 'linux':
        result = subprocess.run([f"{tools_root}/u4pak/target/release/u4pak", *args], capture_output=True, text=True)
    elif sys.platform == 'win32':
        result = subprocess.run([f"{tools_root}/u4pak/target/release/u4pak.exe", *args], capture_output=True, text=True)
    else:
        return print("Se mata negao")
    
    check_result(result)
        
def fix_version(args: list[str]):
    result = subprocess.run([sys.executable, f"{tools_root}/fix_version.py", *args], capture_output=True, text=True)
    
    check_result(result)
        
def load_env_file(filepath: str = ".env"):
    if not os.path.exists(filepath):
        return

    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
                
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                
                os.environ[key] = value
