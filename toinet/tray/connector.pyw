import os
import ctypes
proxy_enable = 1
proxy_server = "socks=127.0.0.1:9051"
os.system('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyEnable /t REG_DWORD /d 1 /f')
os.system('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyServer /t REG_SZ /d "socks=127.0.0.1:9051" /f')
INTERNET_OPTION_SETTINGS_CHANGED = 39
INTERNET_OPTION_REFRESH = 37
internet_set_option = ctypes.windll.Wininet.InternetSetOptionW
internet_set_option(0, INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)
internet_set_option(0, INTERNET_OPTION_REFRESH, 0, 0)
