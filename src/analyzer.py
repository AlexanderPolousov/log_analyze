# src/analyzer.py
import re
import time
from collections import Counter
from functools import partial, reduce
from multiprocessing import Pool, cpu_count
from pathlib import Path
from typing import Tuple

from tqdm import tqdm
from utils.logger import setup_logger


class LogAnalyzer:
    def __init__(self, file_path: str, processes: int = None, log_dir: str = "logs"):
        """
        Инициализация анализатора логов с настройкой логирования
        
        :param file_path: Путь к лог-файлу
        :param processes: Количество процессов (по умолчанию: cpu_count - 1)
        :param log_dir: Директория для хранения логов
        """
        self.file_path = Path(file_path)
        self.processes = processes or max(1, cpu_count() - 1)
        self.chunk_size = 10 * 1024 * 1024  # 10MB на чанк
        
        # Настройка логирования
        log_file = Path(log_dir) / "analysis.log"
        log_file.parent.mkdir(exist_ok=True)
        self.logger = setup_logger("LogAnalyzer", log_file)
        
        # Предкомпилированные регулярные выражения
        self.ip_pattern = re.compile(r'\d+\.\d+\.\d+\.\d+')
        self.status_pattern = re.compile(r'HTTP/\d\.\d"\s(\d{3})')
        
        self.logger.info(
            f"Инициализирован анализатор для {self.file_path} "
            f"(процессов: {self.processes}, чанк: {self.chunk_size//1024//1024}MB)"
        )

    def _read_chunk(self, chunk: str) -> Tuple[Counter, Counter]:
        """
        Обработка одного чанка данных
        
        :param chunk: Блок текста из лог-файла
        :return: Кортеж (Counter IP, Counter статусов)
        """
        ips = []
        statuses = []
        
        for line in chunk.splitlines():
            if not line.strip():
                continue
                
            try:
                ip_match = self.ip_pattern.search(line)
                status_match = self.status_pattern.search(line)
                
                if ip_match:
                    ips.append(ip_match.group())
                if status_match:
                    statuses.append(status_match.group(1))
            except Exception as e:
                self.logger.warning(f"Ошибка парсинга строки: {line[:100]}... ({str(e)})")
                
        return Counter(ips), Counter(statuses)

    def _get_chunks(self):
        """
        Генератор чанков с контролем памяти и обработкой кодировки
        
        :yield: Очередной чанк текста
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8', errors='replace') as f:
                remaining = ''
                while True:
                    chunk = remaining + f.read(self.chunk_size)
                    if not chunk:
                        break
                        
                    last_newline = chunk.rfind('\n')
                    if last_newline == -1:
                        remaining = chunk
                        continue
                        
                    yield chunk[:last_newline]
                    remaining = chunk[last_newline+1:]
                    
                if remaining:
                    yield remaining
                    
        except IOError as e:
            self.logger.error(f"Ошибка чтения файла: {str(e)}")
            raise

    def analyze(self) -> Tuple[Counter, Counter]:
        """
        Основной метод анализа с параллельной обработкой
        
        :return: Кортеж (Counter IP, Counter статусов)
        """
        start_time = time.time()
        self.logger.info("Начало анализа логов")
        
        try:
            with Pool(self.processes) as pool:
                chunks = list(self._get_chunks())
                if not chunks:
                    self.logger.warning("Файл логов пуст")
                    return Counter(), Counter()
                
                self.logger.debug(f"Создано {len(chunks)} чанков для обработки")
                
                # Обработка с прогресс-баром
                results = list(tqdm(
                    pool.imap(self._read_chunk, chunks),
                    total=len(chunks),
                    desc="Обработка чанков",
                    unit="chunk"
                ))
                
                # Агрегация результатов
                total_ips, total_statuses = reduce(
                    lambda acc, x: (acc[0] + x[0], acc[1] + x[1]),
                    results,
                    (Counter(), Counter())
                )
                
                exec_time = time.time() - start_time
                self.logger.info(
                    f"Анализ завершен за {exec_time:.2f} сек. "
                    f"Найдено {len(total_ips)} IP и {len(total_statuses)} статусов"
                )
                
                return total_ips, total_statuses
                
        except Exception as e:
            self.logger.critical(f"Критическая ошибка анализа: {str(e)}", exc_info=True)
            raise