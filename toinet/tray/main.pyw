import sys
import os
import subprocess
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt

AUTO_CONNECTION_FILE = "auto_connection.txt"
TORRC_FILE = "torrc"
ICON_TITLE = "Proxy Launcher"

# Глобальные переменные
proxy_enabled = False
auto_connection = True

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

def toggle_proxy():
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
    update_menu()

def manual_connect():
    run_script("connector.pyw")

def manual_disconnect():
    run_script("disconnector.pyw")

def toggle_auto_connection():
    global auto_connection
    auto_connection = not auto_connection
    write_auto_connection(auto_connection)
    update_menu()

def open_browser_settings():
    open_inet_props()

def manual_settings():
    run_script("maestro.pyw")

def exit_app():
    run_script("disconnector.pyw")
    run_script("closer.pyw")
    log("Exiting...")
    app.quit()

# Глобальные переменные для меню
tray = None
tray_menu = None
toggle_proxy_action = None
toggle_auto_action = None

def update_menu():
    """Обновляет текст пунктов меню"""
    if toggle_proxy_action:
        toggle_proxy_action.setText("Выключить прокси" if proxy_enabled else "Включить прокси")
    if toggle_auto_action:
        toggle_auto_action.setText("Отключить автоподключение" if auto_connection else "Включить автоподключение")

def create_tray_menu():
    global tray, tray_menu, toggle_proxy_action, toggle_auto_action
    
    # Инициализация глобальных переменных
    global proxy_enabled, auto_connection
    auto_connection = read_auto_connection()
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # Создаем иконку трея
    tray = QSystemTrayIcon()

    # Пробуем загрузить иконку, если нет - создаем простую
    try:
        tray.setIcon(QIcon("icon.ico"))
    except:
        # Создаем простую синюю иконку как запасной вариант
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.blue)
        tray.setIcon(QIcon(pixmap))

    tray.setToolTip("Proxy Launcher")

    # Создаем меню
    tray_menu = QMenu()

    # Упрощенная стилизация, которая точно работает
    tray_menu.setStyleSheet("""
        QMenu {
            background-color: #2b2b2b;
            color: white;
            border: 1px solid #555555;
            padding: 5px;
        }
        QMenu::item {
            padding: 5px 20px 5px 20px;
        }
        QMenu::item:selected {
            background-color: #3d3d3d;
        }
        QMenu::separator {
            height: 1px;
            background: #555555;
            margin: 5px 0px 5px 0px;
        }
    """)

    # Создаем действия
    toggle_proxy_action = QAction("Включить прокси", tray_menu)
    connect_action = QAction("Подключиться вручную", tray_menu)
    disconnect_action = QAction("Отключиться вручную", tray_menu)
    toggle_auto_action = QAction("Включить автоподключение", tray_menu)
    browser_settings_action = QAction("Открыть свойства браузера", tray_menu)
    manual_settings_action = QAction("Ручная настройка", tray_menu)
    exit_action = QAction("Выход", tray_menu)

    # Подключаем действия к функциям
    toggle_proxy_action.triggered.connect(toggle_proxy)
    connect_action.triggered.connect(manual_connect)
    disconnect_action.triggered.connect(manual_disconnect)
    toggle_auto_action.triggered.connect(toggle_auto_connection)
    browser_settings_action.triggered.connect(open_browser_settings)
    manual_settings_action.triggered.connect(manual_settings)
    exit_action.triggered.connect(exit_app)

    # Добавляем действия в меню
    tray_menu.addAction(toggle_proxy_action)
    tray_menu.addAction(connect_action)
    tray_menu.addAction(disconnect_action)
    tray_menu.addSeparator()
    tray_menu.addAction(toggle_auto_action)
    tray_menu.addSeparator()
    tray_menu.addAction(browser_settings_action)
    tray_menu.addAction(manual_settings_action)
    tray_menu.addSeparator()
    tray_menu.addAction(exit_action)

    # Устанавливаем контекстное меню
    tray.setContextMenu(tray_menu)
    tray.show()

    # Обновляем текст меню
    update_menu()

    # Показываем сообщение о запуске
    tray.showMessage("Proxy Launcher", "Приложение запущено", QSystemTrayIcon.Information, 1000)

    log("Иконка трея запущена. Нажмите ПКМ на иконке для отображения меню.")

    return app

if __name__ == "__main__":
    app = create_tray_menu()
    sys.exit(app.exec_())