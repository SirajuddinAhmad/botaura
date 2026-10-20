import sys
from datetime import datetime

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False

def _time_str():
    return datetime.now().strftime("%H:%M:%S")

def log_info(message: str):
    if HAS_COLORAMA:
        print(f"{Fore.CYAN}[{_time_str()}]{Fore.RESET} {Fore.BLUE}[INFO]{Fore.RESET} {message}")
    else:
        print(f"[{_time_str()}] [INFO] {message}")

def log_success(message: str):
    if HAS_COLORAMA:
        print(f"{Fore.CYAN}[{_time_str()}]{Fore.RESET} {Fore.GREEN}[SUCCESS]{Fore.RESET} {message}")
    else:
        print(f"[{_time_str()}] [SUCCESS] {message}")

def log_warning(message: str):
    if HAS_COLORAMA:
        print(f"{Fore.CYAN}[{_time_str()}]{Fore.RESET} {Fore.YELLOW}[WARN]{Fore.RESET} {message}")
    else:
        print(f"[{_time_str()}] [WARN] {message}")

def log_error(message: str):
    if HAS_COLORAMA:
        print(f"{Fore.CYAN}[{_time_str()}]{Fore.RESET} {Fore.RED}[ERROR]{Fore.RESET} {message}")
    else:
        print(f"[{_time_str()}] [ERROR] {message}")

def log_wallet(index: int, total: int, address: str):
    masked = address[:6] + "..." + address[-4:] if len(address) > 10 else address
    bar = "=" * 60
    if HAS_COLORAMA:
        print(f"\n{Fore.MAGENTA}{bar}{Fore.RESET}")
        print(f"{Fore.CYAN}[{_time_str()}]{Fore.RESET} {Fore.YELLOW}[WALLET {index}/{total}]{Fore.RESET} {Fore.WHITE}{masked}{Fore.RESET}")
        print(f"{Fore.MAGENTA}{bar}{Fore.RESET}")
    else:
        print(f"\n{bar}")
        print(f"[{_time_str()}] [WALLET {index}/{total}] {masked}")
        print(f"{bar}")

def print_banner():
    banner = r"""
  ==============================================================
    ____  ______      _____      __  ___                 
   / __ \/  _/ /_  __/ ___/___  / __/ /___  ____ _ _____ 
  / / / // // / / / /\__ \/ _ \/ /_/ / __ \/ __ `// ___/ 
 / /_/ // // / /_/ /___/ /  __/ __/ / /_/ / /_/ // /     
/_____/___/_/\__,_//____/\___/_/ /_/\____/\__,_//_/      
                                                          
   GIWA Sepolia (Chain ID: 91342) x AuraLaunch Farmer Bot
  ==============================================================
"""
    if HAS_COLORAMA:
        print(f"{Fore.CYAN}{banner}{Fore.RESET}")
    else:
        print(banner)
