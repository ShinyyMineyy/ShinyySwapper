import os
import sys
import time
import subprocess
from colorama import init, Fore, Style

init(autoreset=True)

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_logo():
    logo = f"""
{Fore.CYAN}╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   {Fore.GREEN}███████╗██╗  ██╗██╗███╗   ██╗██╗   ██╗██╗   ██╗{Fore.CYAN}      ║
║   {Fore.GREEN}██╔════╝██║  ██║██║████╗  ██║╚██╗ ██╔╝╚██╗ ██╔╝{Fore.CYAN}      ║
║   {Fore.GREEN}███████╗███████║██║██╔██╗ ██║ ╚████╔╝  ╚████╔╝ {Fore.CYAN}      ║
║   {Fore.GREEN}╚════██║██╔══██║██║██║╚██╗██║  ╚██╔╝    ╚██╔╝  {Fore.CYAN}      ║
║   {Fore.GREEN}███████║██║  ██║██║██║ ╚████║   ██║      ██║   {Fore.CYAN}      ║
║   {Fore.GREEN}╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝   ╚═╝      ╚═╝   {Fore.CYAN}      ║
║                                                           ║
║              {Fore.YELLOW}S W A P P E R   v2.0{Fore.CYAN}                      ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""
    print(logo)

def progress_bar(current, total, text=""):
    bar_length = 50
    filled = int(bar_length * current / total)
    bar = '█' * filled + '░' * (bar_length - filled)
    percent = int(100 * current / total)
    print(f'\r{Fore.CYAN}[{Fore.GREEN}{bar}{Fore.CYAN}] {Fore.YELLOW}{percent}%{Fore.CYAN} {text}', end='', flush=True)

def animate_loading(text, duration=1.5):
    steps = 30
    for i in range(steps + 1):
        progress_bar(i, steps, text)
        time.sleep(duration / steps)
    print()

def main():
    clear()
    print_logo()
    
    print(f"\n{Fore.CYAN}{'='*63}")
    print(f"{Fore.YELLOW}           INITIALIZING FACE SWAP ENGINE")
    print(f"{Fore.CYAN}{'='*63}\n")
    
    # Step 1: Loading Models
    animate_loading("Loading AI Models...", 2)
    
    # Step 2: Starting Flask
    print(f"\n{Fore.GREEN}✓ Models Loaded Successfully")
    animate_loading("Starting Flask Backend...", 1.5)
    
    # Start Flask minimized
    flask_cmd = 'start /min "Flask Backend" cmd /c ".venv1\\Scripts\\python.exe app_flask.py"'
    subprocess.Popen(flask_cmd, shell=True, cwd=os.path.dirname(os.path.abspath(__file__)))
    
    print(f"\n{Fore.GREEN}✓ Flask Backend Started")
    time.sleep(2)
    
    # Step 3: Starting ngrok
    animate_loading("Starting ngrok Tunnel...", 1.5)
    
    # Start ngrok minimized
    ngrok_cmd = 'start /min "ngrok Tunnel" cmd /c "ngrok config add-authtoken 3ANjJQavBdcQp0rcDNkekJHV1e7_7rZaF8cvzp8fB7EV4cutR && ngrok http 80"'
    subprocess.Popen(ngrok_cmd, shell=True, cwd=os.path.dirname(os.path.abspath(__file__)))
    
    print(f"\n{Fore.GREEN}✓ ngrok Tunnel Started")
    time.sleep(1)
    
    # Final message
    print(f"\n{Fore.CYAN}{'='*63}")
    print(f"{Fore.GREEN}           ALL SYSTEMS OPERATIONAL!")
    print(f"{Fore.CYAN}{'='*63}\n")
    
    print(f"{Fore.YELLOW}  Local:  {Fore.WHITE}http://localhost")
    print(f"{Fore.YELLOW}  Public: {Fore.WHITE}Check ngrok window for URL\n")
    
    print(f"{Fore.CYAN}{'='*63}")
    print(f"{Fore.MAGENTA}  Closing in 3 seconds...")
    print(f"{Fore.CYAN}{'='*63}\n")
    
    time.sleep(3)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.RED}Startup cancelled by user.")
        sys.exit(0)
