# TODO: Refactoring extraction.py

## ✅ Completato
- [x] Estrazione base da singolo file CSV in dict di liste
- [x] Parsing sicuro con `_safe_float` e salto riga header
- [x] Struttura modulare con funzioni dedicate
- [x] Definire costanti stringa per le chiavi (es. `KEY_VOLTAGE`, `KEY_CURRENT`, `KEY_STD`)
- [x] Riscrivere `append_point` come fusione generica tra due dict con validazione delle chiavi (stesso set, stesse lunghezze)

## 🔧 Robustezza & Parsing
- [x] Aggiungere controllo sul numero di campi in `parse_row` (evitare `IndexError` su righe troncate o con delimiter extra)
- [ ] Valutare sostituzione di `.split(',')` con modulo `csv` (gestisce automaticamente spazi, virgolette, righe malformate)
- [x] Gestire `StopIteration` in `next(txt_data)` se il file è vuoto o privo di header

## 🏗️ Architettura & Manutenibilità
- [ ] Aggiungere docstring complete a tutte le funzioni (args, return, edge cases)
- [x] Uniformare i type hints (es. `dict[str, list[float]]` invece di `dict`)
- [ ] Valutare struttura dati dedicata (`dataclass` o `NamedTuple`) per rappresentare un singolo punto misura
- [ ] Sostituire `print()` con `logging` per tracciabilità e disaccoppiamento output/console

## 🧪 Validazione & Testing
- [x] Aggiungere blocco `if __name__ == "__main__":` con esecuzione protetta e path configurabile
- [ ] Preparare file di test sintetici (righe vuote, dati mancanti, formato errato, file vuoto, header assente)
- [ ] Verificare che la propagazione di `NaN` non interrompa i calcoli futuri su `dV/dI`

## 📝 Note
- Mantenere dipendenze esclusivamente da standard library (come da approccio attuale)
- Ogni modifica dovrebbe essere testata incrementalmente prima di passare alla successiva
- La struttura dati in uscita deve restare compatibile con il prossimo step (calcolo derivata + statistiche)