# Docker-команда FROM указывает базовый образ контейнера
# Наш базовый образ - это Linux с предустановленным python
FROM python:3.8.4

ENV APP_HOME /app

# Установим рабочую директорию внутри контейнера
WORKDIR $APP_HOME

# Скопируем остальные файлы в рабочую директорию контейнера
COPY . .

# Установим зависимости внутри контейнера
RUN pip install -r requirements.txt

EXPOSE 3000


# Запустим наше приложение внутри контейнера
ENTRYPOINT ["python", "main.py"]
