import os
import subprocess
import sys
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw

AUTO_CONNECTION_FILE = "auto_connection.txt"
TORRC_FILE = "torrc"
ICON_TITLE = "Proxy Launcher"


def log(msg):
    print(f"[LOG] {msg}")

def read_auto_connection():
    if not os.path.exists(AUTO_CONNECTION_FILE):
        with open(AUTO_CONNECTION_FILE, "w") as f:
            f.write("true")
        return True
    with open(AUTO_CONNECTION_FILE, "r") as f:
        return f.read().strip().lower() == "true"

def write_auto_connection(value: bool):
    with open(AUTO_CONNECTION_FILE, "w") as f:
        f.write("true" if value else "false")

def run_script(script_name):
    if os.path.exists(script_name):
        subprocess.Popen([sys.executable, script_name], creationflags=subprocess.CREATE_NO_WINDOW)
        log(f"Started: {script_name}")
    else:
        log(f"Script not found: {script_name}")

def run_script_blocking(script_name):
    if os.path.exists(script_name):
        subprocess.call([sys.executable, script_name])
        log(f"Ran (blocking): {script_name}")
    else:
        log(f"Script not found: {script_name}")

def open_inet_props():
    subprocess.Popen(["control", "inetcpl.cpl"], shell=True)
    log("Opened Internet Properties")

def create_icon():
    image = Image.new('RGB', (64, 64), "white")
    draw = ImageDraw.Draw(image)
    line_width = 5
    draw.line((16, 16, 48, 48), fill="black", width=line_width+1)
    draw.line((48, 16, 16, 48), fill="black", width=line_width+1)
    draw.line((16, 16, 48, 16), fill="black", width=line_width)

    return image


proxy_enabled = False
auto_connection = read_auto_connection()


def toggle_proxy(icon, item):
    global proxy_enabled
    if not proxy_enabled:
        if not os.path.exists(TORRC_FILE):
            run_script_blocking("auto_maestro.pyw")
        run_script("launcher.pyw")
        if auto_connection:
            run_script("connector.pyw")
        proxy_enabled = True
    else:
        run_script("disconnector.pyw")
        run_script("closer.pyw")
        proxy_enabled = False
    icon.update_menu()

def manual_connect(icon, item):
    run_script("connector.pyw")

def manual_disconnect(icon, item):
    run_script("disconnector.pyw")

def toggle_auto_connection(icon, item):
    global auto_connection
    auto_connection = not auto_connection
    write_auto_connection(auto_connection)
    icon.update_menu()

def open_browser_settings(icon, item):
    open_inet_props()

def manual_settings(icon, item):
    run_script("maestro.pyw")

def exit_app(icon, item):
    run_script("disconnector.pyw")
    run_script("closer.pyw")
    log("Exiting...")
    icon.stop()


def build_menu():
    return Menu(
        MenuItem(
            lambda item: "Выключить прокси" if proxy_enabled else "Включить прокси",
            toggle_proxy
        ),
        MenuItem("Подключиться вручную", manual_connect),
        MenuItem("Отключиться вручную", manual_disconnect),
        MenuItem(
            lambda item: "Отключить автоподключение" if auto_connection else "Включить автоподключение",
            toggle_auto_connection
        ),
        MenuItem("Открыть свойства браузера", open_browser_settings),
        MenuItem("Ручная настройка", manual_settings),
        MenuItem("Выход", exit_app)
    )

if __name__ == "__main__":
    icon = Icon(ICON_TITLE, icon=create_icon(), menu=build_menu())
    log("Starting tray icon...")
    icon.run()

