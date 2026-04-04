import zipfile
import os
import sys

def extract_archive():
    zip_path = r"C:\Users\Alex Bear\Downloads\EvoGenesis-Main.zip"
    extract_path = r"C:\Users\Alex Bear\Downloads\EvoGenesis-Main"
    
    if not os.path.exists(zip_path):
        print(f"Ошибка: Файл не найден по пути {zip_path}")
        sys.exit(1)
        
    print(f"Вскрытие архива: {zip_path}...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        print(f"Успех! Архив извлечен в: {extract_path}")
    except Exception as e:
        print(f"Сбой распаковки: {e}")

if __name__ == "__main__":
    extract_archive()
