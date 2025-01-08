**Projekta apraksts**

### **1. Risinājuma pārskats**

Izstrādāju gan projekta pamata uzdevumu, gan arī papildus izveidoju tīmekļa 
lapu lietotāja saskarnei ar aplikāciju. Varēja arī mēģināt taisīt exe failu
ar ārējo ‘data’ direktoriju, bet ja godīgi – noslinkoju. Tā vietā pievienots
requirements.txt un instalācijas & palaišanas instrukciju.

### **2. Izmantotās tehnoloģijas**

- **Programmēšanas valoda:** `Python`
- **Tīkla ietvars:** `Flask`
- **Datu glabāšanas sistēma:** `SQLite`
- **Datu parsēšana:** `JSON`
- **Lietotāja saskarne:** `HTML`, `CSS`, `JavaScript`

### **3. Datu glabāšana**

Dati tiek glabāti SQLite datu bāzē (fails: `football_stats.db`).

- Spēles dati tiek saglabāti tabulās, kas ietver:
  - Spēlētājus
  - Vārtu guvumus
  - Sarkanās/dzeltenās kartītes
  - Aizvietošanas
  - Komandas

**Tabulu struktūra (saskaņā ar `models.py`)**【39†source】:
- **teams (Komandas)**
  - `id` (INTEGER, PRIMARY KEY)
  - `name` (TEXT, unikāls komandas nosaukums)

- **players (Spēlētāji)**
  - `id` (INTEGER, PRIMARY KEY)
  - `team_id` (INTEGER, REFERENCES teams(id))
  - `number` (INTEGER, spēlētāja numurs komandā)
  - `first_name` (TEXT)
  - `last_name` (TEXT)
  - `role` (TEXT, spēlētāja loma: V, A, U)

- **matches (Spēles)**
  - `id` (INTEGER, PRIMARY KEY)
  - `date` (DATETIME, spēles datums)
  - `venue` (TEXT, spēles norises vieta)
  - `spectators` (INTEGER, skatītāju skaits)
  - `home_team_id` (INTEGER, REFERENCES teams(id))
  - `away_team_id` (INTEGER, REFERENCES teams(id))

- **goals (Vārti)**
  - `id` (INTEGER, PRIMARY KEY)
  - `match_id` (INTEGER, REFERENCES matches(id))
  - `team_id` (INTEGER, REFERENCES teams(id))
  - `scorer_id` (INTEGER, REFERENCES players(id))
  - `assist1_id` (INTEGER, REFERENCES players(id), NULLABLE)
  - `assist2_id` (INTEGER, REFERENCES players(id), NULLABLE)
  - `time` (TEXT, formāts "mm:ss")
  - `is_penalty` (BOOLEAN, vai vārti gūti ar 11m soda sitienu)

- **cards (Kartītes)**
  - `id` (INTEGER, PRIMARY KEY)
  - `match_id` (INTEGER, REFERENCES matches(id))
  - `team_id` (INTEGER, REFERENCES teams(id))
  - `player_id` (INTEGER, REFERENCES players(id))
  - `time` (TEXT, formāts "mm:ss")
  - `is_red` (BOOLEAN, sarkanā kartīte, ja TRUE)

- **substitutions (Aizvietošanas)**
  - `id` (INTEGER, PRIMARY KEY)
  - `match_id` (INTEGER, REFERENCES matches(id))
  - `team_id` (INTEGER, REFERENCES teams(id))
  - `player_out_id` (INTEGER, REFERENCES players(id))
  - `player_in_id` (INTEGER, REFERENCES players(id))
  - `time` (TEXT, formāts "mm:ss")

- **referees (Tiesneši)**
  - `id` (INTEGER, PRIMARY KEY)
  - `first_name` (TEXT)
  - `last_name` (TEXT)

### **4. Datu parsēšana**

Datu parsēšanas process apskata datni `data`, un mēģina parsēt tajā esošos failus. Sistēma izpilda sekojošos soļus:

1. **Fails tiek atvērts un pārbaudīts** - Pārbauda, vai fails nesatur jau reģistrētu spēli
(Vienādi lauki `Vieta`, abi `Komanda` lauki un `Datums`).

2. **Komandu un spēlētāju pirmsapstrāde**:
   - Pārbauda, vai komandas, tiesnesis jau eksistē datu bāzē. Ja nē, tās tiek pievienotas.

3. **Datu saglabāšana**:
   - Visas izmaiņas tiek commitotas datubāzē `src/football_stats.db`


### **5. Sistēmas darbība**

1. Lietotājs vai kāda cita sistēma ievieto jaunus JSON failus datnē `src/data`.
2. Sistēma atpazīst jaunus failus kad tiek palaista un kad lietotājs pieprasa datu atjaunošanu
3. Sistēma pievieno tos datu bāzei.
5. Palaižot skriptu `main.py`, tiek lokāli startēta Flask lietotāja saskarne.
6. Skripts `main.py` arī inicializē datubāzi, ja tā vēl neeksistē.

### **6. Instalācija un atkarības**

Lai nodrošinātu veiksmīgu projekta darbību pēc failu kopēšanas, nepieciešams instalēt visas atkarības (cik briesmīgs tulkojums).

```sh
pip install -r requirements.txt
```

Tas automātiski instalēs Flask, SQLAlchemy un citas nepieciešamās bibliotēkas.