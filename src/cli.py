import argparse
from analyzer import LogAnalyzer
import time
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Оптимизированный анализатор логов')
    parser.add_argument('--file', required=True, type=Path, help='Путь к лог-файлу')
    parser.add_argument('--processes', type=int, help='Количество процессов')
    parser.add_argument('--chunk-size', type=int, default=10, 
                      help='Размер чанка (в MB)')
    args = parser.parse_args()

    if not args.file.exists():
        print(f"Ошибка: Файл {args.file} не найден")
        return

    start_time = time.time()
    
    analyzer = LogAnalyzer(args.file, args.processes)
    analyzer.chunk_size = args.chunk_size * 1024 * 1024
    
    try:
        ips, statuses = analyzer.analyze()
        
        print(f"\nРезультаты ({time.time() - start_time:.2f} сек):")
        print("Топ-5 IP:", ips.most_common(5))
        print("Статусы:", statuses.most_common())
        
    except Exception as e:
        print(f"Ошибка: {str(e)}")

if __name__ == '__main__':
    main()