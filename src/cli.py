import argparse
from analyzer import LogAnalyzer
import time

def main():
    parser = argparse.ArgumentParser(description='Многопроцессорный анализатор логов')
    parser.add_argument('--file', required=True, help='Путь к лог-файлу')
    parser.add_argument('--processes', type=int, help='Количество процессов (по умолчанию: все ядра)')
    args = parser.parse_args()
    
    start_time = time.time()
    analyzer = LogAnalyzer(args.file, args.processes)
    ips, statuses = analyzer.analyze()
    
    print(f"Время обработки: {time.time() - start_time:.2f} сек")
    print("Топ-5 IP:", ips.most_common(5))
    print("Статусы:", statuses)

if __name__ == '__main__':
    main()