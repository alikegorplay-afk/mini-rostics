FROM python:3.13.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Сначала копируем файл с зависимостями
COPY r.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r r.txt

# Копируем остальные файлы
COPY . .

# Запускаем приложение
CMD ["python", "main.py"]