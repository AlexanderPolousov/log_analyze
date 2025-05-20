# generate_logs.py
import random
from datetime import datetime


def generate_nginx_log():
    ip = f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
    date = datetime.now().strftime("%d/%b/%Y:%H:%M:%S")
    methods = ["GET", "POST", "PUT"]
    urls = ["/", "/api", "/login", "/data"]
    status = random.choice([200, 404, 500])
    size = random.randint(100, 5000)
    return f'{ip} - - [{date}] "{random.choice(methods)} {random.choice(urls)} HTTP/1.1" {status} {size}\n'


# Генерируем 1000 записей
with open("data/access.log", "w") as f:
    for _ in range(1000):
        f.write(generate_nginx_log())
