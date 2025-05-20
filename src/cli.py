# src/cli.py
import argparse
from analyzer import LogAnalyzer

def main():
    parser = argparse.ArgumentParser(description='Анализатор логов')
    parser.add_argument('--file', required=True, help='Путь к лог-файлу')
    args = parser.parse_args()
    
    analyzer = LogAnalyzer(args.file)
    print("Топ-5 IP:", analyzer.count_ips().most_common(5))
    print("Статусы:", analyzer.count_status_codes())

if __name__ == '__main__':
    main()