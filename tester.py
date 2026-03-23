import socket
import threading
import time
import argparse
import sys
import signal
from collections import defaultdict
from datetime import datetime

class BandwidthTester:
    def __init__(self, target_ip='127.0.0.1', target_port=12345, 
                 packet_size=1400, num_threads=10, target_mbps=None):
        self.target_ip = target_ip
        self.target_port = target_port
        self.packet_size = packet_size
        self.num_threads = num_threads
        self.target_mbps = target_mbps
        self.running = True
        self.stats = defaultdict(int)
        self.lock = threading.Lock()
        
    def send_packets(self, thread_id):
        """Отправляет пакеты в отдельном потоке"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # Создаем данные пакета фиксированного размера
            payload = f"Thread {thread_id} Packet ".encode()
            payload += b'X' * (self.packet_size - len(payload))
            
            packets_sent = 0
            start_time = time.time()
            
            while self.running:
                try:
                    sock.sendto(payload, (self.target_ip, self.target_port))
                    packets_sent += 1
                    
                    # Обновляем статистику
                    with self.lock:
                        self.stats[thread_id] = packets_sent
                    
                    # Если задан лимит скорости, добавляем задержку
                    if self.target_mbps:
                        elapsed = time.time() - start_time
                        expected_packets = (self.target_mbps * 1024 * 1024 * elapsed) / (self.packet_size * 8)
                        if packets_sent > expected_packets:
                            time.sleep(0.0001)  # Микро-задержка для контроля скорости
                            
                except socket.error as e:
                    print(f"Ошибка сокета в потоке {thread_id}: {e}")
                    break
                    
        except Exception as e:
            print(f"Ошибка в потоке {thread_id}: {e}")
        finally:
            sock.close()
    
    def print_stats(self):
        """Выводит статистику трафика"""
        while self.running:
            time.sleep(1)
            with self.lock:
                total_packets = sum(self.stats.values())
                if total_packets > 0:
                    # Расчет скорости
                    total_bytes = total_packets * self.packet_size
                    mbps = (total_bytes * 8) / (1024 * 1024)
                    
                    print(f"\r[{datetime.now().strftime('%H:%M:%S')}] "
                          f"Пакетов: {total_packets:,} | "
                          f"Скорость: {mbps:.2f} Мбит/с | "
                          f"Потоков: {self.num_threads}", end='', flush=True)
    
    def stop(self, signum=None, frame=None):
        """Останавливает все потоки"""
        print("\n\nОстановка тестирования...")
        self.running = False
    
    def run(self):
        """Запускает тестирование"""
        print(f"Запуск тестирования пропускной способности")
        print(f"Цель: {self.target_ip}:{self.target_port}")
        print(f"Размер пакета: {self.packet_size} байт")
        print(f"Количество потоков: {self.num_threads}")
        if self.target_mbps:
            print(f"Целевая скорость: {self.target_mbps} Мбит/с")
        else:
            print("Режим: Максимальная нагрузка")
        print("Нажмите Ctrl+C для остановки\n")
        
        # Обработчик сигнала для graceful shutdown
        signal.signal(signal.SIGINT, self.stop)
        
        # Создаем и запускаем потоки
        threads = []
        for i in range(self.num_threads):
            thread = threading.Thread(target=self.send_packets, args=(i,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Запускаем поток статистики
        stats_thread = threading.Thread(target=self.print_stats)
        stats_thread.daemon = True
        stats_thread.start()
        
        try:
            # Ждем завершения
            while self.running:
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            self.stop()
        
        # Финальная статистика
        print("\n\nФинальная статистика:")
        total_packets = sum(self.stats.values())
        if total_packets > 0:
            total_bytes = total_packets * self.packet_size
            mbps = (total_bytes * 8) / (1024 * 1024)
            print(f"Всего отправлено пакетов: {total_packets:,}")
            print(f"Всего отправлено данных: {total_bytes / (1024*1024):.2f} МБ")
            print(f"Средняя скорость: {mbps:.2f} Мбит/с")

def main():
    parser = argparse.ArgumentParser(description='Тестировщик пропускной способности сети')
    parser.add_argument('-i', '--ip', default='127.0.0.1', 
                       help='IP адрес получателя (по умолчанию: 127.0.0.1)')
    parser.add_argument('-p', '--port', type=int, default=12345,
                       help='Порт получателя (по умолчанию: 12345)')
    parser.add_argument('-s', '--size', type=int, default=1400,
                       help='Размер пакета в байтах (по умолчанию: 1400)')
    parser.add_argument('-t', '--threads', type=int, default=10,
                       help='Количество потоков (по умолчанию: 10)')
    parser.add_argument('-b', '--bandwidth', type=float, default=None,
                       help='Целевая скорость в Мбит/с (по умолчанию: максимальная)')
    
    args = parser.parse_args()
    
    # Проверка параметров
    if args.threads < 1:
        print("Ошибка: количество потоков должно быть >= 1")
        sys.exit(1)
    
    if args.size < 1 or args.size > 65507:  # Максимальный размер UDP пакета
        print("Ошибка: размер пакета должен быть от 1 до 65507 байт")
        sys.exit(1)
    
    if args.bandwidth is not None and args.bandwidth <= 0:
        print("Ошибка: целевая скорость должна быть > 0 Мбит/с")
        sys.exit(1)
    
    # Создаем и запускаем тестер
    tester = BandwidthTester(
        target_ip=args.ip,
        target_port=args.port,
        packet_size=args.size,
        num_threads=args.threads,
        target_mbps=args.bandwidth
    )
    
    tester.run()

if __name__ == "__main__":
    main()