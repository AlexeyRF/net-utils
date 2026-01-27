import os
import subprocess
import signal
import sys
import time
from pathlib import Path
PROJECT_FOLDER = Path(__file__).parent.absolute()
TOR_EXE = "tor.exe"
GEOIP_FOLDER = PROJECT_FOLDER / "data"
LYREBIRD_EXE = PROJECT_FOLDER / "tor" / "pluggable_transports" / "lyrebird.exe"
def generate_torrc():
    torrc_content = f"""
DataDirectory {PROJECT_FOLDER}
GeoIPFile {GEOIP_FOLDER / "geoip"}
GeoIPv6File {GEOIP_FOLDER / "geoip6"}
SocksPort 0.0.0.0:9050
ExitNodes {{us}},{{de}},{{fr}},{{nl}},{{se}}
UseBridges 1
Bridge ВАШ МОСТ ЗДЕСЬ
Bridge ВАШ МОСТ ЗДЕСЬ
ClientTransportPlugin meek_lite,obfs2,obfs3,obfs4,scramblesuit,webtunnel exec {LYREBIRD_EXE}
AvoidDiskWrites 1
HardwareAccel 1
ClientOnly 1
AutomapHostsOnResolve 1
SafeLogging 1
"""
    torrc_path = PROJECT_FOLDER / "torrc"
    torrc_path.write_text(torrc_content.strip())
    return torrc_path
def run_tor(torrc_path):
    tor_path = PROJECT_FOLDER / TOR_EXE
    if not tor_path.exists():
        raise FileNotFoundError(f"Tor не найден: {tor_path}")
    process = subprocess.Popen(
        [str(tor_path), "-f", str(torrc_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    def log_stream(stream):
        for line in stream:
            print(line, end="")
    import threading
    threading.Thread(target=log_stream, args=(process.stdout,), daemon=True).start()
    threading.Thread(target=log_stream, args=(process.stderr,), daemon=True).start()
    return process
def main():
    print("Генерация...")
    torrc_path = generate_torrc()
    print(f"Файл конфигурации: {torrc_path}")
    print("Запуск...")
    tor_process = run_tor(torrc_path)
    def signal_handler(sig, frame):
        print("\nОстановка...")
        tor_process.terminate()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    print("Tor запущен. Ctrl+C для остановки.")
    while True:
        time.sleep(1)
if __name__ == "__main__":
    main()
