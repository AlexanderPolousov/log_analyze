# tests/conftest.py
import pytest
from src.analyzer import LogAnalyzer


@pytest.fixture
def sample_log(tmp_path):
    """Создает тестовый лог-файл"""
    log_data = """192.168.1.1 - - [10/Oct/2023:12:00:00 +0300] "GET / HTTP/1.1" 200 1234
10.0.0.1 - - [10/Oct/2023:12:00:01 +0300] "POST /api HTTP/1.1" 404 5678
192.168.1.1 - - [10/Oct/2023:12:00:02 +0300] "GET /favicon.ico HTTP/1.1" 200 8910"""

    log_file = tmp_path / "test.log"
    log_file.write_text(log_data)
    return log_file


@pytest.fixture
def analyzer(sample_log):
    """Фикстура анализатора с тестовыми данными"""
    return LogAnalyzer(sample_log, processes=1)
