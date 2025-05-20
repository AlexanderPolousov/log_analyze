# src/analyzer.py
import re
from collections import Counter

class LogAnalyzer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.log_data = self._read_file()
    
    def _read_file(self):
        with open(self.file_path, 'r') as f:
            return f.readlines()
    
    def count_ips(self):
        ips = [re.findall(r'\d+\.\d+\.\d+\.\d+', line)[0] 
               for line in self.log_data if re.findall(r'\d+\.\d+\.\d+\.\d+', line)]
        return Counter(ips)
    
    def count_status_codes(self):
        statuses = [re.findall(r'HTTP/\d\.\d"\s(\d{3})', line)[0] 
                    for line in self.log_data if re.findall(r'HTTP/\d\.\d"\s(\d{3})', line)]
        return Counter(statuses)