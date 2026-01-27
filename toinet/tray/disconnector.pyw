import os
import ctypes
os.system('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0 /f')
os.system('reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyServer /f')
INTERNET_OPTION_SETTINGS_CHANGED = 39
INTERNET_OPTION_REFRESH = 37
internet_set_option = ctypes.windll.Wininet.InternetSetOptionW
internet_set_option(0, INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)
internet_set_option(0, INTERNET_OPTION_REFRESH, 0, 0)
