from pathlib import Path
import re

raw_dataset_path = Path(__file__).parent

DRY_RUN = False  # metti False quando vuoi davvero rinominare

pattern = re.compile(
    r"E14_FS_(?P<pressure>[\dE\-]+)_(?P<temp>(\d+C|rt))_(?P<date>\d{6})_(?P<time>\d{6})\.txt"
)

def convert_date(date_str):
    # da DDMMYY → YYYYMMDD (assumiamo 2000+)
    day = date_str[:2]
    month = date_str[2:4]
    year = "20" + date_str[4:]
    return f"{year}{month}{day}"

def convert_temp(temp_str):
    if temp_str == "rt":
        return "020C"
    else:
        value = int(temp_str.replace("C", ""))
        return f"{value:03d}C"

for file in raw_dataset_path.iterdir():
    if file.suffix != '.txt':
        continue

    match = pattern.match(file.name)
    if not match:
        print(f"[SKIP] Nome non riconosciuto: {file.name}")
        continue

    pressure = match.group("pressure")
    temp = match.group("temp")
    date = match.group("date")
    time = match.group("time")

    new_date = convert_date(date)
    new_temp = convert_temp(temp)

    new_name = f"{new_date}_{time}_E14FS_P{pressure}mbar_T{new_temp}.txt"
    new_path = file.parent / new_name

    if new_path.exists():
        print(f"[SKIP] Esiste già: {new_name}")
        continue

    print(f"{file.name}  →  {new_name}")

    if not DRY_RUN:
        file.rename(new_path)