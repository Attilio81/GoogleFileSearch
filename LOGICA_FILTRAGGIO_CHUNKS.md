# Logica di Filtraggio dei Chunks

## Problema Identificato

**Domanda utente**: "Perché mi trova tutti i documenti? E come decidi quali 15 chunk mandare a Gemini?"

### Il Comportamento Precedente

1. **Ricerca semantica** recupera 25 chunk da tutti i documenti attivi
2. **Nessun filtro per rilevanza** - venivano presi i primi 15 senza guardare lo score
3. **Risultato**: fonti non pertinenti nella sezione "Fonti consultate"

### Perché Trova Tutti i Documenti?

**I metadati NON filtrano la ricerca!**

Se hai caricato documenti con metadato `Progetto: "Leonardo"`, questo:
- ✅ **Viene indicizzato nel testo** - può essere trovato nelle query semantiche
- ❌ **NON filtra automaticamente** - l'API cerca in TUTTI i documenti attivi

L'API Google File Search fa ricerca semantica sul **contenuto dei chunk**, non sui metadati come criterio di filtro.

---

## Nuova Logica di Filtraggio

### 1. Fase di Retrieval (Query)

```
Query utente → Google File Search API
    ↓
Recupera fino a RESULTS_COUNT chunks (default: 25)
    ↓
Ogni chunk ha un "chunkRelevanceScore" (0.0 - 1.0)
    ↓
Ordinati per score decrescente
```

**Parametro configurabile**: `RESULTS_COUNT` in `.env` (default: 25)

### 2. Fase di Filtraggio (Pre-Generation)

```
25 chunks recuperati
    ↓
Filtra per MIN_RELEVANCE_SCORE (default: 0.3)
    ↓ 
Esempio: 17 chunks con score >= 0.3
    ↓
Prendi i primi MAX_CHUNKS_FOR_GENERATION (default: 15)
    ↓
15 chunks inviati a Gemini
```

**Parametri configurabili**:
- `MIN_RELEVANCE_SCORE`: soglia minima di rilevanza (0.0-1.0)
- `MAX_CHUNKS_FOR_GENERATION`: massimo chunks per generazione (1-25)

### 3. Fase di Generazione

```
15 chunks → Contesto per Gemini
    ↓
Gemini genera risposta sintetizzata
    ↓
Frontend mostra fonti dei 15 chunks usati
```

---

## Come Funziona il Relevance Score

Il `chunkRelevanceScore` è calcolato da Google File Search basandosi su:

1. **Similarità semantica**: embedding della query vs. embedding del chunk
2. **Distanza coseno**: misura angolo tra vettori (0.0 = opposti, 1.0 = identici)
3. **Ranking**: chunks ordinati per similarità decrescente

**Esempio pratico**:

Query: "Quanto costa la pittura murale?"

```
Chunk 1: "Pittura murale 4€/mq" → Score: 0.85 ✅ Molto rilevante
Chunk 2: "Pittura interna"      → Score: 0.42 ✅ Rilevante
Chunk 3: "Muratura esterna"     → Score: 0.28 ❌ Poco rilevante
Chunk 4: "Progetto Leonardo"    → Score: 0.15 ❌ Non rilevante
```

Con `MIN_RELEVANCE_SCORE = 0.3`:
- ✅ Chunk 1 e 2 passano il filtro
- ❌ Chunk 3 e 4 vengono scartati

---

## Configurazione Consigliata

### Per Documenti Tecnici/Manuali (DEFAULT)

```properties
RESULTS_COUNT=25
MIN_RELEVANCE_SCORE=0.3
MAX_CHUNKS_FOR_GENERATION=15
```

**Risultato**: 
- Recupera 25 chunks più rilevanti
- Filtra quelli con score < 0.3
- Usa top 15 per generazione
- **Fonti mostrate**: ~10-15 documenti

### Per Query Semplici (FAQ/Ricerche Veloci)

```properties
RESULTS_COUNT=15
MIN_RELEVANCE_SCORE=0.4
MAX_CHUNKS_FOR_GENERATION=10
```

**Risultato**:
- Recupera solo 15 chunks
- Filtra più aggressivamente (score >= 0.4)
- Usa top 10 per generazione
- **Fonti mostrate**: ~5-8 documenti

### Per Domande Complesse (Analisi Multi-Documento)

```properties
RESULTS_COUNT=40
MIN_RELEVANCE_SCORE=0.2
MAX_CHUNKS_FOR_GENERATION=20
```

**Risultato**:
- Recupera più contesto (40 chunks)
- Filtro permissivo (score >= 0.2)
- Usa fino a 20 chunks per generazione
- **Fonti mostrate**: ~15-20 documenti

---

## Cosa Vedere nei Log

Dopo il riavvio del server, quando fai una query vedrai:

```
INFO - Chunk recuperati: 25, Score >= 0.3: 17, Usati per generazione: 15
```

**Interpretazione**:
- **25**: chunks totali recuperati dalla ricerca semantica
- **17**: chunks che superano la soglia MIN_RELEVANCE_SCORE
- **15**: chunks effettivamente inviati a Gemini (limitati da MAX_CHUNKS_FOR_GENERATION)

**Le fonti mostrate nel frontend saranno solo quelle dei 15 chunks usati!**

---

## Perché Questa Logica?

### Vantaggi del Doppio Filtro

1. **Filtro per Score (MIN_RELEVANCE_SCORE)**:
   - Elimina chunks non pertinenti
   - Riduce "rumore" nella risposta
   - Migliora precisione delle fonti

2. **Limite Numerico (MAX_CHUNKS_FOR_GENERATION)**:
   - Velocizza generazione (meno token)
   - Riduce costi API
   - Semplifica visualizzazione fonti
   - Evita "information overload" per Gemini

### Quando Modificare i Parametri

**Aumenta MIN_RELEVANCE_SCORE** se:
- Vedi troppi documenti non pertinenti nelle fonti
- Vuoi risposte più focalizzate
- Hai molti documenti con contenuto simile

**Diminuisci MIN_RELEVANCE_SCORE** se:
- Perdi informazioni importanti
- I documenti hanno contenuto molto vario
- Fai query generiche che richiedono contesto ampio

**Aumenta MAX_CHUNKS_FOR_GENERATION** se:
- La risposta è troppo superficiale
- Serve confrontare informazioni da più documenti
- Domande complesse tipo "confronta prezzi tra tutti i preventivi"

**Diminuisci MAX_CHUNKS_FOR_GENERATION** se:
- La risposta è troppo lunga o confusa
- Troppe fonti rendono difficile identificare quella giusta
- Query semplici che non richiedono molto contesto

---

## Test Pratico

1. **Riavvia il server**:
   ```bash
   cd backend
   .\start_server.bat
   ```

2. **Verifica configurazione**:
   ```bash
   curl http://localhost:5000/api/config
   ```
   
   Dovresti vedere:
   ```json
   {
     "min_relevance_score": 0.3,
     "max_chunks_for_generation": 15,
     "results_count": 25
   }
   ```

3. **Fai una query** e controlla i log:
   ```
   ✅ Recuperati 25 chunk rilevanti
   INFO - Chunk recuperati: 25, Score >= 0.3: 17, Usati per generazione: 15
   ```

4. **Verifica le fonti** nel frontend:
   - Dovrebbero essere ridotte rispetto a prima
   - Solo documenti effettivamente rilevanti
   - Numero coerente con i log (~15 chunks = ~10-15 documenti)

---

## Risoluzione Problemi

### "Recupera sempre 17 chunks invece di 25"

**Possibili cause**:
1. Google API potrebbe avere un limite interno per documento
2. Non ci sono abbastanza chunks rilevanti (score troppo basso)
3. I documenti hanno meno di 25 chunks totali

**Verifica**:
- Controlla quanti chunks ha ogni documento (frontend → modal chunks)
- Prova query più generiche per vedere se recupera di più
- Guarda i relevance score nei log (potrebbero essere tutti bassi)

### "Fonti sempre tutte uguali"

**Causa**: Tutti i documenti hanno contenuto simile (es. tutti hanno "Progetto Leonardo" nei metadati)

**Soluzione**:
- Aumenta MIN_RELEVANCE_SCORE a 0.4-0.5 per filtrare meglio
- Fai query più specifiche (es. "codice articolo XYZ" invece di "Leonardo")
- Considera di NON mettere metadati comuni in tutti i documenti

### "Risposta troppo generica"

**Causa**: Troppi chunks diluiscono il contesto

**Soluzione**:
- Riduci MAX_CHUNKS_FOR_GENERATION a 10
- Aumenta MIN_RELEVANCE_SCORE a 0.4
- Fai query più specifiche

---

## Prossimi Sviluppi

### Filtro per Metadati (TODO)

Aggiungere parametro `metadata_filter` per cercare solo in documenti con metadati specifici:

```python
# Esempio futuro
query_payload = {
    'query': query_text,
    'resultsCount': results_count,
    'metadata_filter': {
        'Progetto': 'Leonardo',
        'Tipo': 'Preventivo'
    }
}
```

Attualmente **non supportato** dall'API Google File Search.

### UI per Regolare Soglie

Aggiungere slider nel frontend per:
- MIN_RELEVANCE_SCORE (0.0 - 1.0)
- MAX_CHUNKS_FOR_GENERATION (1 - 25)

Permettere all'utente di sperimentare in tempo reale.

### Visualizzazione Score

Mostrare il relevance score accanto ad ogni fonte nel frontend:

```
📄 Preventivo_Edile.pdf (Score: 0.85) ★★★★★
📄 Manuale_Tecnico.pdf (Score: 0.42) ★★☆☆☆
```

---

## Conclusione

La nuova logica:

1. ✅ **Filtra per rilevanza** - solo chunks con score sufficiente
2. ✅ **Limita intelligentemente** - top N chunks più rilevanti
3. ✅ **Configurabile** - via `.env` senza modificare codice
4. ✅ **Trasparente** - log dettagliati per debugging
5. ✅ **Riduce rumore** - meno fonti non pertinenti mostrate

**Risultato**: Risposte più focalizzate e fonti più coerenti! 🎯
