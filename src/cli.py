#!/usr/bin/env python3
# src/cli.py
import argparse
import logging
import sys
from pathlib import Path

from analyzer import LogAnalyzer


def parse_args():
    """Настройка парсера аргументов командной строки"""
    parser = argparse.ArgumentParser(
        description="Многопроцессорный анализатор логов с продвинутым логированием",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Основные параметры
    parser.add_argument(
        "--file", type=Path, required=True, help="Путь к анализируемому лог-файлу"
    )
    parser.add_argument(
        "--processes",
        type=int,
        help="Количество worker-процессов (по умолчанию: CPU-1)",
    )
    parser.add_argument(
        "--chunk-size", type=int, default=10, help="Размер чанка для обработки (в MB)"
    )

    # Настройки логирования
    parser.add_argument(
        "--log-dir", type=Path, default="logs", help="Директория для хранения логов"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Уровень детализации логов",
    )
    parser.add_argument(
        "--no-console-log", action="store_true", help="Отключить вывод логов в консоль"
    )

    return parser.parse_args()


def validate_file(file_path: Path) -> bool:
    """Проверка существования и доступности файла"""
    if not file_path.exists():
        logging.error(f"Файл {file_path} не существует")
        return False
    if not file_path.is_file():
        logging.error(f"{file_path} не является файлом")
        return False
    if file_path.stat().st_size == 0:
        logging.warning("Файл логов пуст")
    return True


def setup_logging(log_dir: Path, log_level: str, no_console: bool) -> None:
    """Глобальная настройка логирования"""
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "cli.log", encoding="utf-8"),
            *([] if no_console else [logging.StreamHandler(sys.stdout)]),
        ],
    )


def main():
    try:
        args = parse_args()
        setup_logging(args.log_dir, args.log_level, args.no_console_log)
        logging.info(f"Запуск анализатора с параметрами: {vars(args)}")

        if not validate_file(args.file):
            sys.exit(1)

        analyzer = LogAnalyzer(
            file_path=args.file, processes=args.processes, log_dir=args.log_dir
        )
        analyzer.chunk_size = args.chunk_size * 1024 * 1024

        ips, statuses = analyzer.analyze()

        # Вывод результатов
        print("\nРезультаты анализа:")
        print("Топ-5 IP-адресов:", ips.most_common(5))
        print("Распределение статусов:", statuses.most_common())

    except Exception as e:
        logging.critical(f"Фатальная ошибка: {str(e)}", exc_info=True)
        sys.exit(1)
    finally:
        logging.info("Анализатор завершил работу")


if __name__ == "__main__":
    main()
