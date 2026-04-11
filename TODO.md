# TODO: Analisi Curve I(V)

## ✅ Completato
- [x] Definire il percorso della cartella con `pathlib.Path`
- [x] Aprire i file `.txt` con `with open(...)`
- [x] Estrarre i dati e organizzarli in `{'voltage': [], 'current': [], 'std_dev': []}`

## 📋 Prossimi Passi
- [ ] Iterare su tutti i file `*.txt` presenti nella cartella
- [ ] Estrarre il valore di temperatura dal nome di ciascun file
- [ ] Calcolare numericamente la resistenza puntuale
- [ ] Calcolare statistiche aggregate per file
- [ ] Strutturare i risultati in righe/colonne coerenti per l'export
- [ ] Salvare il file di output in formato CSV con nome chiaro
- [ ] Aggiungere gestione errori di base (file vuoti, formato inatteso, encoding)
- [ ] Validare l'output confrontando un caso noto o controllando coerenza fisica

## 📝 Note
- Input: file `.txt` in formato CSV (V, I, std_dev)
- Output: file `.txt`/`.csv` con statistiche di `dV/dI` + temperatura per misura
- Librerie: standard Python (aggiungere solo se necessario e deciso autonomamente)
- Metodo di derivazione: da definire in base alla stabilità dei dati