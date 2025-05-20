# src/analyzer.py
import re
from collections import Counter
from multiprocessing import Pool, cpu_count
from functools import partial, reduce  # Явный импорт reduce
from tqdm import tqdm

class LogAnalyzer:
    def __init__(self, file_path, processes=None):
        self.file_path = file_path
        self.processes = processes or max(1, cpu_count() - 1)  # Оставляем 1 ядро системе
        self.chunk_size = 10 * 1024 * 1024  # 10MB
        self.ip_pattern = re.compile(r'\d+\.\d+\.\d+\.\d+')  # Предкомпилированные
        self.status_pattern = re.compile(r'HTTP/\d\.\d"\s(\d{3})')  # регулярки

    def _read_chunk(self, chunk):
        ips = []
        statuses = []
        
        for line in chunk.splitlines():
            if not line.strip():  # Пропускаем пустые строки
                continue
                
            ip_match = self.ip_pattern.search(line)
            status_match = self.status_pattern.search(line)
            
            if ip_match:
                ips.append(ip_match.group())
            if status_match:
                statuses.append(status_match.group(1))
                
        return Counter(ips), Counter(statuses)

    def _get_chunks(self):
        """Генератор с обработкой крайних случаев"""
        with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
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

    def analyze(self):
        try:
            with Pool(self.processes) as pool:
                chunks = list(self._get_chunks())
                if not chunks:
                    return Counter(), Counter()
                    
                results = list(tqdm(
                    pool.imap(self._read_chunk, chunks),
                    total=len(chunks),
                    desc="Анализ логов",
                    unit="chunk"
                ))
                
                return reduce(
                    lambda acc, x: (acc[0] + x[0], acc[1] + x[1]),
                    results,
                    (Counter(), Counter())
                )
                
        except Exception as e:
            print(f"Ошибка при анализе: {str(e)}")
            return Counter(), Counter()