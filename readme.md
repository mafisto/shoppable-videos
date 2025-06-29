# Запуск приложения:
требуется создать .env файл на основе .env.example

ключ можно взять здесь:
* https://hailuoai.video




### docker-compose up --build

# Тестирование:

### Загрузить изображение:
    curl -X POST -F "file=@product.jpg" http://localhost:8000/upload

### Проверить статус: 
    curl http://localhost:8000/status/d6a98b8d-6b9a-4a2c-9e1d-3b7f6a8c5d9b

### Получить видео (после завершения обработки): 
    curl -OJ http://localhost:8000/video/d6a98b8d-6b9a-4a2c-9e1d-3b7f6a8c5d9b