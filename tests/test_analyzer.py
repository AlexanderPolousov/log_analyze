# tests/test_analyzer.py
import pytest
from collections import Counter


def test_ip_counter(analyzer):
    ips, _ = analyzer.analyze()
    assert ips == Counter({"192.168.1.1": 2, "10.0.0.1": 1})


def test_status_counter(analyzer):
    _, statuses = analyzer.analyze()
    assert statuses == Counter({"200": 2, "404": 1})


def test_empty_file(tmp_path):
    empty_file = tmp_path / "empty.log"
    empty_file.touch()

    analyzer = LogAnalyzer(empty_file)
    ips, statuses = analyzer.analyze()

    assert not ips and not statuses


def test_invalid_lines(tmp_path, caplog):
    log_file = tmp_path / "invalid.log"
    log_file.write_text("INVALID_LINE\n" * 10)

    analyzer = LogAnalyzer(log_file)
    analyzer.analyze()

    assert "Ошибка парсинга строки" in caplog.text


@pytest.mark.parametrize("processes", [1, 2])
def test_multiprocessing(sample_log, processes):
    analyzer = LogAnalyzer(sample_log, processes=processes)
    ips, statuses = analyzer.analyze()

    assert len(ips) == 2  # 2 уникальных IP
    assert sum(statuses.values()) == 3  # Всего 3 записи
