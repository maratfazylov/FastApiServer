#!/usr/bin/env python
"""
Скрипт для тестирования FastAPI сервера загрузки файлов
"""

import os
import sys
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"

def check_server():
    """Проверяет, запущен ли сервер"""
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Сервер доступен")
            return True
        else:
            print(f"❌ Сервер вернул статус: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Ошибка соединения: {e}")
        print("❌ Сервер недоступен. Запустите его командой: py server.py")
        return False
    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")
        return False

def upload_video():
    """Загружает видео с котиком"""
    video_path = Path("cat_video.mp4")
    
    if not video_path.exists():
        print(f"❌ Файл {video_path} не найден.")
        print("Пожалуйста, скачайте видео с котиком и сохраните его как cat_video.mp4")
        return None
    
    print(f"📤 Загрузка видео {video_path}...")
    
    try:
        with open(video_path, 'rb') as video_file:
            files = {'file': (video_path.name, video_file, 'video/mp4')}
            response = requests.put(
                f"{BASE_URL}/api/upload",
                params={"file_type": "video"},
                files=files
            )
            
            if response.status_code == 200:
                result = response.json()
                uuid = result.get('uuid')
                print(f"✅ Видео успешно загружено с UUID: {uuid}")
                
                # Сохраним UUID в файл для будущего использования
                with open("last_uploaded_uuid.txt", "w") as uuid_file:
                    uuid_file.write(uuid)
                
                return uuid
            else:
                print(f"❌ Ошибка при загрузке видео: {response.status_code}")
                print(response.text)
                return None
    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")
        return None

def download_file(uuid, output_path):
    """Скачивает файл по UUID"""
    print(f"📥 Скачивание файла с UUID {uuid}...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/{uuid}")
        
        if response.status_code == 200:
            with open(output_path, 'wb') as out_file:
                out_file.write(response.content)
            print(f"✅ Файл успешно скачан и сохранен как {output_path}")
            return True
        else:
            print(f"❌ Ошибка при скачивании файла: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")
        return False

def upload_image():
    """Загружает изображение с котиком"""
    image_path = Path("cat_image.jpg")
    
    if not image_path.exists():
        print(f"❌ Файл {image_path} не найден.")
        print("Пожалуйста, скачайте изображение с котиком и сохраните его как cat_image.jpg")
        return None
    
    print(f"📤 Загрузка изображения {image_path}...")
    
    try:
        with open(image_path, 'rb') as image_file:
            files = {'file': (image_path.name, image_file, 'image/jpeg')}
            response = requests.put(
                f"{BASE_URL}/api/upload",
                params={"file_type": "image"},
                files=files
            )
            
            if response.status_code == 200:
                result = response.json()
                uuid = result.get('uuid')
                print(f"✅ Изображение успешно загружено с UUID: {uuid}")
                return uuid
            else:
                print(f"❌ Ошибка при загрузке изображения: {response.status_code}")
                print(response.text)
                return None
    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")
        return None

def download_thumbnail(uuid, width, height, output_path):
    """Скачивает превью изображения с заданными размерами"""
    print(f"🖼️ Скачивание превью размером {width}x{height}...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/{uuid}",
            params={"width": width, "height": height}
        )
        
        if response.status_code == 200:
            with open(output_path, 'wb') as out_file:
                out_file.write(response.content)
            print(f"✅ Превью успешно скачано и сохранено как {output_path}")
            return True
        else:
            print(f"❌ Ошибка при скачивании превью: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")
        return False

def main():
    """Основная функция тестирования API"""
    print("=== 🚀 Тестирование FastAPI File Upload Service ===\n")
    
    # Проверяем доступность сервера
    if not check_server():
        sys.exit(1)
    
    print("\n--- 📹 Тестирование загрузки и получения видео ---")
    # Загружаем видео
    video_uuid = upload_video()
    if not video_uuid:
        print("❌ Не удалось получить UUID видео. Пропускаем следующий тест.")
    else:
        # Скачиваем видео
        download_file(video_uuid, "downloaded_cat_video.mp4")
    
    print("\n--- 🖼️ Тестирование загрузки и получения изображения ---")
    # Загружаем изображение
    image_uuid = upload_image()
    if not image_uuid:
        print("❌ Не удалось получить UUID изображения. Пропускаем тест превью.")
    else:
        # Скачиваем превью
        download_thumbnail(image_uuid, 200, 200, "cat_image_thumbnail.jpg")
    
    print("\n=== ✅ Тестирование завершено ===")

if __name__ == "__main__":
    main() 