from pathlib import Path
import re

# ==============================
# CONFIGURAZIONE
# ==============================

DATASET_PATH = Path(__file__).parent
DRY_RUN = False  # Metti False per applicare le modifiche


# ==============================
# REGEX PATTERN
# ==============================

pattern = re.compile(
    r"""
    (?P<sample>[A-Za-z0-9]+)            # Nome campione (senza underscore)
    _P(?P<pressure>[\dE\-]+torr)        # Pressione (es. 4E-2torr)
    _T(?P<temp>(\d+C|rt))               # Temperatura (es. 550C o rt)
    (?:_(?P<config>AB|BA))?             # Configurazione VdP opzionale
    _(?P<date>\d{6})                    # Data (DDMMYY)
    _(?P<time>\d{6})                    # Ora (HHMMSS)
    \.txt
    """,
    re.VERBOSE
)


# ==============================
# FUNZIONI DI SUPPORTO
# ==============================

def convert_date(date_str: str) -> str:
    """
    Converte una data dal formato DDMMYY a YYYYMMDD.

    Assunzione:
        - Tutte le date sono nel XXI secolo (2000+)

    Args:
        date_str (str): Data nel formato DDMMYY (es. '170426').

    Returns:
        str: Data nel formato YYYYMMDD (es. '20260417').
    """
    day = date_str[:2]
    month = date_str[2:4]
    year = "20" + date_str[4:]
    return f"{year}{month}{day}"


def convert_temperature(temp_str: str) -> str:
    """
    Converte la temperatura in formato standard TnnnC.

    Regole:
        - 'rt' → '020C'
        - valori numerici → padding a 3 cifre (es. 50C → 050C)

    Args:
        temp_str (str): Temperatura (es. '50C' o 'rt').

    Returns:
        str: Temperatura formattata (es. '050C', '020C').
    """
    if temp_str == "rt":
        return "020C"

    value = int(temp_str.replace("C", ""))
    return f"{value:03d}C"


# ==============================
# FUNZIONE PRINCIPALE
# ==============================

def rename_measurement_files(directory: Path, dry_run: bool = True) -> None:
    """
    Rinomina i file di misura in una directory secondo uno standard coerente.

    Formato input atteso:
        SAMPLE_P...torr_T...C[_AB/BA]_DDMMYY_HHMMSS.txt

    Formato output:
        YYYYMMDD_HHMMSS_SAMPLE_P...torr_T...C[_AB/BA].txt

    Caratteristiche:
        - Supporta configurazioni Van der Pauw (AB/BA) opzionali
        - Converte 'rt' → 'T020C'
        - Applica padding alla temperatura (T050C, T550C, ...)
        - Converte la data in formato ISO-like (YYYYMMDD)
        - Evita overwrite di file esistenti
        - Modalità dry-run per verifica preventiva

    Args:
        directory (Path): Percorso della directory contenente i file.
        dry_run (bool): Se True, non esegue il rename ma stampa le operazioni.

    Returns:
        None
    """
    for file in directory.iterdir():
        if file.suffix != ".txt":
            continue

        match = pattern.match(file.name)
        if not match:
            print(f"[SKIP] Nome non riconosciuto: {file.name}")
            continue

        sample = match.group("sample")
        pressure = match.group("pressure")
        temp = match.group("temp")
        config = match.group("config")  # può essere None
        date = match.group("date")
        time = match.group("time")

        new_date = convert_date(date)
        new_temp = convert_temperature(temp)

        # Costruzione nome base
        new_name = f"{new_date}_{time}_{sample}_P{pressure}_T{new_temp}"

        # Aggiunta configurazione VdP se presente
        if config:
            new_name += f"_{config}"

        new_name += ".txt"

        new_path = file.parent / new_name

        if new_path.exists():
            print(f"[SKIP] Esiste già: {new_name}")
            continue

        print(f"{file.name}  →  {new_name}")

        if not dry_run:
            file.rename(new_path)


# ==============================
# ESECUZIONE
# ==============================

if __name__ == "__main__":
    rename_measurement_files(DATASET_PATH, dry_run=DRY_RUN)