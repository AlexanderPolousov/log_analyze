import re
from collections import Counter
from multiprocessing import Pool, cpu_count
import os

class LogAnalyzer:
    def __init__(self, file_path, processes=None):
        self.file_path = file_path
        self.processes = processes or cpu_count()
    
    def _read_chunk(self, chunk):
        lines = chunk.split('\n')
        ips = []
        statuses = []
        for line in lines:
            ip_match = re.findall(r'\d+\.\d+\.\d+\.\d+', line)
            status_match = re.findall(r'HTTP/\d\.\d"\s(\d{3})', line)
            if ip_match:
                ips.append(ip_match[0])
            if status_match:
                statuses.append(status_match[0])
        return Counter(ips), Counter(statuses)

    def analyze(self):
        with open(self.file_path, 'r') as f:
            content = f.read()
        
        # Делим файл на чанки по процессам
        chunk_size = len(content) // self.processes
        chunks = [
            content[i * chunk_size: (i + 1) * chunk_size] 
            for i in range(self.processes)
        ]
        
        with Pool(self.processes) as pool:
            results = pool.map(self._read_chunk, chunks)
        
        # Агрегируем результаты
        total_ips = Counter()
        total_statuses = Counter()
        for ips, statuses in results:
            total_ips.update(ips)
            total_statuses.update(statuses)
        
        return total_ips, total_statuses