from pathlib import Path

directory_path = Path(__file__).parent

for file in sorted(directory_path.glob("*.txt")):
    print(file.name)