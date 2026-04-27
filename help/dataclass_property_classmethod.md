# Dataclass, `@property` e `@classmethod`: una guida concettuale

*Riferimento: `models.py` — modelli per misure di trasporto elettrico (Van der Pauw)*

---

## Il problema che questo codice risolve

Prima di entrare nei meccanismi, vale la pena capire cosa succederebbe senza di loro.
Immaginate di dover rappresentare i metadati di una misura: campione, timestamp, pressione,
temperatura, allineamento. L'approccio più immediato è un dizionario:

```python
metadata = {
    "sample": "S42",
    "timestamp": datetime(2024, 3, 15, 10, 30),
    "pressure_torr": 1e-5,
    "temperature_k": 300.0,
    "alignment": "VDP_A"
}
```

Funziona, ma porta con sé tre problemi concreti. Primo: nessuna garanzia sui tipi — nulla
impedisce che `temperature_k` contenga la stringa `"ambient"` invece di un float. Secondo:
nessuna struttura visibile nel codice; chi legge deve esplorare ogni dizionario per capire
quali chiavi esistono. Terzo: non c'è modo di associare comportamenti (metodi) ai dati.

Le classi risolvono questi problemi, ma scrivere `__init__`, `__repr__` e `__eq__` per ogni
struttura dati è verboso e ripetitivo. È esattamente il disagio che `@dataclass` elimina.

---

## `@dataclass`: una classe senza il boilerplate

Un decoratore in Python è una funzione che trasforma un'altra funzione (o classe). La sintassi
`@nome_decoratore` applicata a una classe equivale a scrivere `NomeClasse = nome_decoratore(NomeClasse)`.
`@dataclass` è un decoratore di classe fornito dalla libreria standard (modulo `dataclasses`)
che legge le annotazioni di tipo presenti nel corpo della classe e genera automaticamente
`__init__`, `__repr__` ed `__eq__`.

In `models.py`, `Metadata` è definita così:

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Metadata:
    sample: str
    timestamp: datetime
    pressure_torr: float
    temperature_k: float
    alignment: str | None
```

Queste cinque righe fanno sì che Python generi automaticamente un costruttore equivalente a:

```python
def __init__(self, sample: str, timestamp: datetime,
             pressure_torr: float, temperature_k: float,
             alignment: str | None):
    self.sample = sample
    self.timestamp = timestamp
    self.pressure_torr = pressure_torr
    self.temperature_k = temperature_k
    self.alignment = alignment
```

Viene generato anche un `__repr__` che produce una stringa leggibile quando si stampa l'oggetto,
e un `__eq__` che confronta due istanze campo per campo. Tutto senza una riga scritta a mano.

Le annotazioni di tipo (`: str`, `: float`, `str | None`) sono parte integrante del meccanismo:
`@dataclass` le usa per determinare l'ordine e i nomi dei parametri del costruttore. Non impongono
controlli a runtime (Python non è un linguaggio tipizzato staticamente), ma documentano l'intenzione
e abilitano strumenti di analisi statica come `mypy` o `pyright`.

Il caso `str | None` per `alignment` esprime che il campo può contenere una stringa oppure
il valore `None` (nessun allineamento specificato). È la notazione introdotta in Python 3.10;
nelle versioni precedenti si scriveva `Optional[str]` importando da `typing`.

### Validazione in `__post_init__`

`@dataclass` genera `__init__`, ma lascia un punto di aggancio per logica aggiuntiva: il metodo
speciale `__post_init__`, che viene chiamato automaticamente alla fine del costruttore generato.
In `models.py`, `Measurement` lo usa per verificare che il DataFrame contenga le colonne attese:

```python
@dataclass
class Measurement:
    data: pd.DataFrame

    def __post_init__(self):
        required = ColumnNames.required()
        missing = required - set(self.data.columns)
        if missing:
            raise ValueError(f"Missing columns: {missing}")
```

L'espressione `required - set(self.data.columns)` è una sottrazione insiemistica: restituisce
gli elementi presenti in `required` ma assenti nelle colonne del DataFrame. Se l'insieme risultante
non è vuoto, l'oggetto non può essere costruito in uno stato valido e viene sollevata un'eccezione.
Questo è un pattern importante: non lasciare che l'oggetto esista in uno stato incoerente.

---

## `@property`: attributi con comportamento

Una `@property` permette di definire un metodo che si comporta come un attributo in lettura.
Chi accede a `oggetto.nome_property` non vede una chiamata a funzione, ma ottiene un valore
calcolato al momento dell'accesso.

La distinzione tra attributo e property è concettuale prima che sintattica. Un attributo è un
valore memorizzato; una property è un valore derivato o calcolato. In `models.py`, `Measurement`
espone le singole colonne del DataFrame interno come property:

```python
@property
def voltage(self) -> pd.Series:
    return self.data[ColumnNames.VOLTAGE]

@property
def current(self) -> pd.Series:
    return self.data[ColumnNames.CURRENT]
```

Senza `@property`, per ottenere la colonna delle tensioni bisognerebbe scrivere
`misura.data[ColumnNames.VOLTAGE]` ogni volta, esponendo il dettaglio implementativo (che i dati
sono in un DataFrame con certi nomi di colonna). Con `@property`, si scrive semplicemente
`misura.voltage`, e l'implementazione interna può cambiare senza che il codice chiamante
se ne accorga.

In `LinearFit`, `@property` serve per calcolare quantità fisicamente significative a partire
dai parametri del fit:

```python
@dataclass
class LinearFit:
    slope: float
    intercept: float
    r_squared: float

    @property
    def resistance(self) -> float:
        """Resistenza in Ohm. Assume che il fit sia I(V)."""
        return 1 / self.slope if self.slope != 0 else float('inf')

    @property
    def conductance(self) -> float:
        """Conduttanza in Siemens."""
        return self.slope
```

`resistance` non è memorizzata: viene calcolata ogni volta che viene acceduta. Se `slope`
cambiasse (in una versione mutabile della classe), `resistance` restituirebbe automaticamente
il valore aggiornato. Questa è la forza delle property: il codice chiamante scrive
`fit.resistance` come se fosse un dato, ma sotto c'è una funzione.

Un dettaglio da notare: `@property` è compatibile con `@dataclass`. Le property non vengono
incluse tra i campi del costruttore generato da `@dataclass` (che considera solo le annotazioni
di tipo nel corpo della classe, non i metodi), quindi non c'è conflitto.

---

## `@classmethod`: costruttori alternativi

Un metodo normale riceve come primo argomento `self`, cioè l'istanza su cui è chiamato.
Un `@classmethod` riceve invece `cls`, cioè la classe stessa. Questo lo rende indipendente
da qualsiasi istanza e quindi chiamabile direttamente sulla classe: `NomeClasse.metodo()`.

L'uso più comune (e quello presente in `models.py`) è il **costruttore alternativo**: un modo
diverso di creare un oggetto, a partire da una forma di input diversa dall'`__init__` standard.

```python
@classmethod
def from_dataframe(cls, df: pd.DataFrame):
    return cls(data=df[[ColumnNames.VOLTAGE, ColumnNames.CURRENT,
                         ColumnNames.STD_DEV, ColumnNames.DELAY]].copy())
```

Questo metodo prende un DataFrame grezzo (che potrebbe avere molte più colonne del necessario),
estrae solo le colonne rilevanti, ne fa una copia, e costruisce un oggetto `Measurement` pulito.
La chiamata `cls(data=...)` equivale a `Measurement(data=...)`, ma usando `cls` si garantisce
che il metodo funzioni correttamente anche in presenza di sottoclassi: se `Measurement` venisse
esteso, `cls` si riferirebbe alla sottoclasse, non alla classe base.

Il pattern dei costruttori alternativi con `@classmethod` è idiomatico in Python. Si trovano
nella libreria standard (ad esempio, `datetime.fromtimestamp()`, `datetime.fromisoformat()`)
e in molte librerie di terze parti. Il prefisso `from_` nella convenzione di denominazione
è largamente seguito: comunica che il metodo crea un'istanza a partire da una certa
rappresentazione dell'input.

---

## Una nota critica: `@dataclass` e la mutabilità

`@dataclass` genera oggetti mutabili per impostazione predefinita: è possibile modificare
i campi dopo la costruzione. Questo va bene in molti contesti, ma può sorprendere quando si
usano dataclass come chiavi di dizionari o elementi di insiemi. Un oggetto mutabile non è
hashable per default, il che significa che Python solleva `TypeError` se si prova a inserirlo
in un `set` o usarlo come chiave.

```python
from dataclasses import dataclass

@dataclass
class Punto:
    x: float
    y: float

p = Punto(1.0, 2.0)

# Questo fallisce:
# s = {p}  # TypeError: unhashable type: 'Punto'
```

Se si ha bisogno di oggetti immutabili e hashable, si usa `@dataclass(frozen=True)`. Con
`frozen=True`, i campi non possono essere modificati dopo la costruzione, e Python genera
automaticamente `__hash__`. In `models.py` questa opzione non è usata, il che è appropriato:
le strutture dati rappresentano misure in elaborazione, dove poter aggiornare i campi ha senso.

Un secondo comportamento da conoscere: `@dataclass` non gestisce i campi con valori di default
mutabili in modo diverso dalle classi normali. Scrivere `campo: list = []` come valore di
default in una dataclass è un errore che Python rileva e segnala esplicitamente. Il motivo è
che un singolo oggetto lista verrebbe condiviso tra tutte le istanze. La soluzione è usare
`field(default_factory=list)`:

```python
from dataclasses import dataclass, field

@dataclass
class Contenitore:
    elementi: list = field(default_factory=list)  # Corretto: ogni istanza ha la sua lista
```

---

## Dove si trovano questi pattern nel codice reale

Le `@dataclass` sono oggi lo strumento standard in Python per rappresentare strutture dati
con tipo definito. Le si trova in API client (per modellare richieste e risposte), in pipeline
di dati scientifici (esattamente come in `models.py`), in configurazioni di applicazione,
e come oggetti di trasferimento dati (DTO) in architetture a strati.

Le `@property` sono ubique in qualsiasi codebase orientata agli oggetti ben progettata.
Ogni volta che un oggetto ha un attributo che dipende logicamente da altri attributi, o
che richiede validazione o trasformazione in lettura, una property è lo strumento giusto.
La libreria `pandas` stessa le usa estensivamente (ad esempio, `DataFrame.shape`, `DataFrame.dtypes`).

I `@classmethod` come costruttori alternativi si trovano in quasi ogni libreria Python matura.
La sequenza `__init__` per il caso base e uno o più `from_*` per input specializzati è un
pattern di progettazione consolidato che rende le classi più flessibili senza appesantire
il costruttore principale con logica condizionale.

Chi vuole approfondire può esplorare `@staticmethod` (simile a `@classmethod`, ma non riceve
né `self` né `cls`) e il modulo `dataclasses` nella documentazione ufficiale, che include
opzioni come `field()`, `__post_init__`, `KW_ONLY` e `InitVar` per scenari più articolati.
