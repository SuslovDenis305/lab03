#SuslovDenis305
import os
import shapefile
import json
import csv
import sys
import requests
import zipfile
from tqdm import tqdm

def downloadCoastline():
    # URL для скачивания файла
    url = "https://naciscdn.org/naturalearth/10m/cultural/ne_10m_populated_places.zip"

    # Папка для сохранения файлов
    folder = "countries"

    # Создание папки, если ее нет
    if not os.path.exists(folder):
        os.makedirs(folder)
    else:
        # Очистка папки, если она уже существует
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

    # Загрузка файла
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get("content-length", 0))
    block_size = 1024  # 1 KB
    progress_bar = tqdm(total=total_size, unit="B", unit_scale=True)

    with open(os.path.join(folder, "ne_10m_populated_places.zip"), "wb") as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)

    progress_bar.close()
    print("Распаковка архива")
    # Разархивирование файла
    zip_path = os.path.join(folder, "ne_10m_populated_places.zip")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(folder)

    # Удаление zip-архива
    os.remove(zip_path)

def shp_to_json(input_shp, output_json):
    reader = shapefile.Reader(input_shp)
    fields = reader.fields[1:]
    field_names = [field[0] for field in fields]
    data = []
    for sr in reader.shapeRecords():
        atr = dict(zip(field_names, sr.record))
        geom = sr.shape.__geo_interface__
        data.append({"properties": atr, "geometry": geom})
#SuslovDenis305
    with open(output_json, 'w') as json_file:
        json.dump(data, json_file, indent=4)

    print(f"Сконвертировано: {input_shp}")


def json_to_csv(input_json, output_csv):
    with open(input_json, 'r') as json_file:
        data = json.load(json_file)

    with open(output_csv, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)

        # Запись CSV заголовка
        header = ["NAME", "latitude", "longitude"]
        writer.writerow(header)

        # Запись строк data
        for item in data:
            properties = item["properties"]
            geometry = item["geometry"]
            writer.writerow([properties["NAME"], geometry["coordinates"][1], geometry["coordinates"][0]])

downloadCoastline()

# Входная папка содержит файлы SHP, выходная папка для файлов JSON и CSV
input_folder = "countries"
output_folder = "countries/output_convert"

# Создание выходной папки, если она не существует
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Получение списка всех SHP-файлов во входной папке
shp_files = [file for file in os.listdir(input_folder) if file.lower().endswith(".shp")]

total_files = len(shp_files)
processed_files = 0

# Выполнение итерации по каждому SHP-файлу и выполнение конвертации
for shp_file in shp_files:
    processed_files += 1
    print(f"Конвиртируется в файл {processed_files}/{total_files}: {shp_file}")

    # Создание путей для входных и выходных файлов
    input_shp = os.path.join(input_folder, shp_file)
    output_json = os.path.join(output_folder, f"{os.path.splitext(shp_file)[0]}.json")
    output_csv = os.path.join(output_folder, f"{os.path.splitext(shp_file)[0]}.csv")

    # Выполнение конвертации
    shp_to_json(input_shp, output_json)
    json_to_csv(output_json, output_csv)

print("Конвертация из CSV завершена.")
