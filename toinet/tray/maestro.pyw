import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
europe = {
    "Австрия": "at", "Бельгия": "be", "Болгария": "bg", "Хорватия": "hr", "Кипр": "cy", "Чехия": "cz",
    "Дания": "dk", "Эстония": "ee", "Финляндия": "fi", "Франция": "fr", "Германия": "de", "Греция": "gr",
    "Венгрия": "hu", "Исландия": "is", "Ирландия": "ie", "Италия": "it", "Латвия": "lv", "Литва": "lt",
    "Люксембург": "lu", "Мальта": "mt", "Нидерланды": "nl", "Норвегия": "no", "Польша": "pl", "Португалия": "pt",
    "Румыния": "ro", "Словакия": "sk", "Словения": "si", "Испания": "es", "Швеция": "se", "Швейцария": "ch"
}
nato = {
    "США": "us", "Канада": "ca", "Великобритания": "gb", "Турция": "tr", "Чехия": "cz", "Польша": "pl",
    "Германия": "de", "Франция": "fr", "Италия": "it", "Нидерланды": "nl", "Испания": "es", "Норвегия": "no"
}
sng = {
    "Россия": "ru", "Беларусь": "by", "Казахстан": "kz", "Узбекистан": "uz", "Таджикистан": "tj",
    "Кыргызия": "kg", "Армения": "am", "Азербайджан": "az", "Молдавия": "md"
}
commonwealth = {
    "Австралия": "au", "Канада": "ca", "Великобритания": "gb", "Новая Зеландия": "nz", "Индия": "in",
    "ЮАР": "za", "Сингапур": "sg"
}
all_countries = {**europe, **nato, **sng, **commonwealth}
class TorrcGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Конфигуратор")
        self.geometry("600x300")
        self.data_dir = tk.StringVar(value=os.path.join(os.getcwd(), "data"))
        self.geoip_path = tk.StringVar()
        self.geoipv6_path = tk.StringVar()
        self.create_widgets()
    def create_widgets(self):
        row = 0
        tk.Label(self, text="Выберите страны выхода:").grid(row=row, column=0, sticky='w')
        self.country_list = tk.Listbox(self, selectmode='multiple', height=10)
        for name in sorted(all_countries.keys()):
            self.country_list.insert(tk.END, name)
        self.country_list.grid(row=row, column=1, sticky='w')
        row += 1
        tk.Label(self, text="Файл с мостами (bridges.txt):").grid(row=row, column=0, sticky='w')
        self.bridge_entry = tk.Entry(self, width=60)
        self.bridge_entry.grid(row=row, column=1, sticky='w')
        tk.Button(self, text="Обзор", command=self.browse_bridges).grid(row=row, column=2)
        row += 1
        tk.Label(self, text="DataDirectory:").grid(row=row, column=0, sticky='w')
        tk.Entry(self, textvariable=self.data_dir, width=60).grid(row=row, column=1)
        tk.Button(self, text="Обзор", command=self.browse_data_dir).grid(row=row, column=2)
        row += 1
        tk.Label(self, text="GeoIP файл:").grid(row=row, column=0, sticky='w')
        tk.Entry(self, textvariable=self.geoip_path, width=60).grid(row=row, column=1)
        tk.Button(self, text="Обзор", command=lambda: self.browse_file(self.geoip_path)).grid(row=row, column=2)
        row += 1
        tk.Label(self, text="GeoIPv6 файл:").grid(row=row, column=0, sticky='w')
        tk.Entry(self, textvariable=self.geoipv6_path, width=60).grid(row=row, column=1)
        tk.Button(self, text="Обзор", command=lambda: self.browse_file(self.geoipv6_path)).grid(row=row, column=2)
        row += 1
        tk.Button(self, text="Создать настройку", command=self.generate_torrc).grid(row=row, column=1)
    def browse_bridges(self):
        path = filedialog.askopenfilename(title="Выберите файл bridges.txt")
        if path:
            self.bridge_entry.delete(0, tk.END)
            self.bridge_entry.insert(0, path)
    def browse_data_dir(self):
        path = filedialog.askdirectory(title="Выберите папку для DataDirectory")
        if path: self.data_dir.set(path)
    def browse_file(self, var):
        path = filedialog.askopenfilename(title="Выберите файл")
        if path: var.set(path)
    def generate_torrc(self):
        selected_indices = self.country_list.curselection()
        country_codes = [all_countries[self.country_list.get(i)] for i in selected_indices]
        bridges_path = self.bridge_entry.get()
        try:
            with open(bridges_path, 'r', encoding='utf-8') as f: bridges = f.read().strip().splitlines()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать bridges.txt: {e}")
            return
        torrc = [
            f"DataDirectory {self.data_dir.get()}",
            f"GeoIPFile {self.geoip_path.get()}",
            f"GeoIPv6File {self.geoipv6_path.get()}",
            "SocksPort 9051",
            f"ExitNodes {','.join(f'{{{code}}}' for code in country_codes)}",
            "UseBridges 1",
            '\n'.join(f"Bridge {bridge}" for bridge in bridges),
            f"ClientTransportPlugin meek_lite,obfs2,obfs3,obfs4,scramblesuit,webtunnel exec {Path.cwd()}"'\\tor\\pluggable_transports\\lyrebird.exe',
            "AvoidDiskWrites 1",
            "HardwareAccel 1",
            "ClientOnly 1",
            "AutomapHostsOnResolve 1",
            "SafeLogging 1",  
        ]
        try:
            with open("torrc", "w", encoding='utf-8') as f: f.write('\n'.join(torrc))
            messagebox.showinfo("Готово", "Конфигурация успешно создана.")
        except Exception as e: messagebox.showerror("Ошибка", f"Не удалось записать: {e}")
if __name__ == '__main__':
    app = TorrcGUI()
    app.mainloop()
