# Запуск приложения:
* ~~требуется создать .env файл на основе .env.example~~

 * docker-compose up --build


### Загрузить изображение:
    curl -X POST -F "file=@product.jpg" http://localhost:8000/upload

    response = {
                "session_id": "08315bac-d213-4a1d-8006-d97f13b87442"
            }

### Получить видео (после завершения обработки): 
    curl -J http://localhost:8000/video/08315bac-d213-4a1d-8006-d97f13b87442

    response = {
                "status": "Completed",
                "url": "http://test.mp4"
                }