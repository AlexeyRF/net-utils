"""
import subprocess
import os
import sys

project_dir = os.path.abspath(os.path.dirname(__file__))
tor_exe_path = os.path.join(project_dir, 'tor', 'tor.exe')
torrc_path = os.path.join(project_dir, 'torrc')

if not os.path.exists(tor_exe_path):
    sys.exit(1)

if not os.path.exists(torrc_path):
    sys.exit(1)

try:
    process = subprocess.Popen(
        [tor_exe_path, '-f', torrc_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,  
        universal_newlines=True,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    
    while True:
        output = process.stdout.readline()
        error = process.stderr.readline()
        
        if output == '' and error == '' and process.poll() is not None:
            break
            
    return_code = process.poll()

except Exception as e:
    sys.exit(1)

import subprocess
import os
import sys
from pathlib import Path
import threading

project_dir = Path(__file__).parent.absolute()
tor_exe_path = project_dir / 'tor' / 'tor.exe'
torrc_path = project_dir / 'torrc'

if not tor_exe_path.exists():
    sys.exit("Tor исполняемый файл не найден.")

if not torrc_path.exists():
    sys.exit("Файл конфигурации torrc не найден.")

def log_stream(stream):
    for line in stream:
        pass  # или print(line, end="") если нужен вывод

try:
    process = subprocess.Popen(
        [str(tor_exe_path), '-f', str(torrc_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True  # то же, что universal_newlines=True
        #creationflags=subprocess.CREATE_NO_WINDOW
    )

    threading.Thread(target=log_stream, args=(process.stdout,), daemon=True).start()
    threading.Thread(target=log_stream, args=(process.stderr,), daemon=True).start()

except Exception as e:
    sys.exit(f"Ошибка запуска Tor: {e}")

# процесс просто остаётся жить
print("Tor запущен.")
try:
    while True:
        pass
except KeyboardInterrupt:
    print("Остановка Tor...")
    process.terminate()
    sys.exit(0)
"""
import subprocess
import sys
from pathlib import Path

project_dir = Path(__file__).parent.absolute()
tor_exe_path = project_dir / 'tor' / 'tor.exe'
torrc_path = project_dir / 'torrc'

if not tor_exe_path.exists():
    sys.exit("Tor exe not found")

if not torrc_path.exists():
    sys.exit("torrc not found")

try:
    process = subprocess.Popen(
        [str(tor_exe_path), '-f', str(torrc_path)],
        stdout=subprocess.DEVNULL,  # не читаем stdout
        stderr=subprocess.DEVNULL,  # не читаем stderr
        creationflags=subprocess.CREATE_NO_WINDOW
    )
except Exception as e:
    sys.exit(f"Failed to start Tor: {e}")

print("Tor started without console window.")
try:
    process.wait()
except KeyboardInterrupt:
    print("Stopping Tor...")
    process.terminate()
