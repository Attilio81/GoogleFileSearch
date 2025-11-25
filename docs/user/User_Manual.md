# Manuale Utente - Sistema di Gestione Documenti con AI

## 📋 Indice

1. [Introduzione](#introduzione)
2. [Accesso al Sistema](#accesso-al-sistema)
3. [Interfaccia Utente](#interfaccia-utente)
4. [Gestione Documenti](#gestione-documenti)
5. [Ricerca nei Documenti](#ricerca-nei-documenti)
6. [Chat Intelligente](#chat-intelligente)
7. [Interpretare i Risultati](#interpretare-i-risultati)
8. [Impostazioni](#impostazioni)
9. [Best Practices](#best-practices)
10. [Risoluzione Problemi](#risoluzione-problemi)
11. [FAQ](#faq)

---

## Introduzione

### Cos'è questo sistema?

Il **Sistema di Gestione Documenti con AI** è una piattaforma intelligente che ti permette di:

- 📁 **Caricare documenti** (PDF, Word, Excel, presentazioni)
- 🔍 **Cercare informazioni** all'interno di tutti i tuoi documenti contemporaneamente
- 💬 **Chattare con i documenti** facendo domande in linguaggio naturale
- 📊 **Ricevere risposte precise** con citazione delle fonti

### Come funziona?

Il sistema utilizza **Google Gemini AI** per:
1. Analizzare e indicizzare i tuoi documenti
2. Comprendere le tue domande in italiano
3. Trovare le informazioni rilevanti
4. Generare risposte precise con citazione delle fonti

---

## Accesso al Sistema

### Requisiti

- **Browser**: Chrome, Firefox, Safari o Edge (versione recente)
- **Connessione**: Internet stabile
- **Risoluzione**: Minimo 1280x720px (consigliato 1920x1080)

### URL di Accesso

```
http://localhost:3001
```

> **Nota**: L'URL può variare in base alla configurazione aziendale. Contatta l'amministratore di sistema per l'URL corretto.

### Prima Connessione

1. Apri il browser
2. Inserisci l'URL fornito
3. Vedrai la schermata principale con tre sezioni:
   - **Documenti** (gestione upload)
   - **Ricerca Chunks** (ricerca avanzata)
   - **Chat** (conversazione con i documenti)

---

## Interfaccia Utente

### Layout Principale

L'interfaccia è divisa in tre pagine principali accessibili dal menu laterale:

#### 📄 Documenti
- Visualizza tutti i documenti caricati
- Carica nuovi documenti
- Elimina documenti esistenti
- Monitora lo stato di elaborazione

#### 🔎 Ricerca Chunks
- Cerca informazioni specifiche
- Visualizza sezioni rilevanti dei documenti
- Filtra per score di rilevanza

#### 💬 Chat
- Conversazione naturale con i tuoi documenti
- Risposte generate dall'AI con fonti
- Cronologia conversazione
- Streaming in tempo reale

---

## Gestione Documenti

### Caricare un Documento

1. **Vai alla sezione "Documenti"**
2. **Clicca su "Carica Documento"** o trascina il file nell'area di upload
3. **Seleziona il file** dal tuo computer
4. **Attendi l'elaborazione**:
   - ⏳ Stato: `PROCESSING` (in elaborazione)
   - ✅ Stato: `ACTIVE` (pronto per la ricerca)
   - ❌ Stato: `FAILED` (errore nel caricamento)

![Interfaccia di Upload](images/documents_upload.png)

### Formati Supportati

✅ **Documenti di Testo:**
- PDF (`.pdf`)
- Word (`.doc`, `.docx`)
- Excel (`.xls`, `.xlsx`)
- PowerPoint (`.ppt`, `.pptx`)
- File di testo (`.txt`)

✅ **Altri Formati:**
- HTML (`.html`, `.htm`)
- Markdown (`.md`)

> **Limite dimensione**: 20 MB per file

### Best Practices per i Documenti

#### ✅ Documenti Ottimali

- **PDF nativi** (non scansioni)
- **Testo ben formattato** con titoli e paragrafi
- **Nomi file descrittivi**: `Manuale_Barriere_Vapore_2025.pdf` invece di `doc1.pdf`
- **Contenuto testuale** (non solo immagini)

#### ❌ Evita

- PDF scansionati senza OCR
- Documenti protetti da password
- File corrotti o illeggibili
- Nomi file generici (`prev.pdf`, `doc.pdf`)

### Monitorare lo Stato dei Documenti

Nella lista documenti vedrai:

| Stato | Significato | Azione |
|-------|-------------|--------|
| ⏳ `PROCESSING` | In elaborazione | Attendi (30-60 sec) |
| ✅ `ACTIVE` | Pronto per la ricerca | Puoi interrogarlo |
| ❌ `FAILED` | Errore | Ricarica il documento |

### Eliminare un Documento

1. **Trova il documento** nella lista
2. **Clicca sull'icona cestino** 🗑️
3. **Conferma l'eliminazione**

> ⚠️ **Attenzione**: L'eliminazione è permanente!

---

## Ricerca nei Documenti

### Ricerca Chunks (Sezioni)

La ricerca chunks trova **sezioni specifiche** dei documenti che contengono le informazioni cercate.

#### Come Fare una Ricerca

1. **Vai alla sezione "Ricerca Chunks"**
2. **Inserisci la query** (es: "barriere a vapore composizione")
3. **Clicca "Cerca"**
4. **Visualizza i risultati** ordinati per rilevanza

#### Interpretare i Risultati

Ogni risultato mostra:

```
┌─────────────────────────────────────────┐
│ 📄 Manuale_Barriere_Vapore.pdf          │
│ 🎯 Score: 87%                            │
│                                          │
│ Contenuto:                               │
│ "La barriera a vapore è composta da...   │
│  bitume modificato con polimeri SBS..."  │
└─────────────────────────────────────────┘
```

**Score di Rilevanza:**
- **80-100%**: Molto rilevante, risponde direttamente alla tua domanda
- **65-79%**: Rilevante, contiene informazioni utili
- **50-64%**: Poco rilevante, correlazione debole
- **< 50%**: Non rilevante (filtrato automaticamente)

#### Tips per Ricerche Efficaci

✅ **Buone Query:**
- "Composizione barriere a vapore"
- "Costi impermeabilizzazione terrazzo"
- "Installazione pannelli isolanti spessore"

❌ **Query Poco Efficaci:**
- "barriera" (troppo generico)
- "quanto costa?" (manca contesto)
- "BV installazione" (usa abbreviazioni)

---

## Chat Intelligente

### Come Funziona la Chat

La chat utilizza l'AI per:
1. **Comprendere** la tua domanda
2. **Cercare** nei documenti caricati
3. **Generare** una risposta completa
4. **Citare** le fonti utilizzate

### Fare una Domanda

1. **Vai alla sezione "Chat"**
2. **Scrivi la domanda** nella casella di input
3. **Premi Invio** o clicca l'icona invio ✉️
4. **Attendi la risposta**:
   - Vedrai tre puntini animati (⋯) mentre l'AI elabora
   - La risposta apparirà progressivamente (streaming)

![Interfaccia Chat](images/chat_interface.png)

### Esempi di Domande Efficaci

#### 💡 Domande Specifiche

```
✅ "Quali sono le caratteristiche tecniche delle barriere a vapore?"
✅ "Quanto costa l'impermeabilizzazione di un terrazzo di 100 mq?"
✅ "Come si installa un pannello isolante?"
```

#### 💡 Domande di Confronto

```
✅ "Qual è la differenza tra barriera a vapore e membrana traspirante?"
✅ "Confronta i prezzi dei materiali nel preventivo A e B"
```

#### 💡 Domande di Sintesi

```
✅ "Riassumi le caratteristiche principali del prodotto X"
✅ "Elenca i passaggi per l'installazione"
```

#### ❌ Domande Poco Efficaci

```
❌ "Dimmi tutto" (troppo generico)
❌ "Quanto costa?" (manca contesto: cosa?)
❌ "BV specs" (usa linguaggio naturale, non abbreviazioni)
```

### Conversazioni Multi-Turn

Puoi fare **domande di follow-up** mantenendo il contesto:

```
Tu: "Parlami delle barriere a vapore"
AI: [Risposta dettagliata...]

Tu: "Quanto costano?"
AI: [Risposta sui costi, mantenendo il contesto "barriere a vapore"]

Tu: "Come si installano?"
AI: [Risposta sull'installazione...]
```

> **Nota**: Il sistema mantiene solo le **ultime 2 domande** per ottimizzare le prestazioni.

### Interrompere una Risposta

Se la risposta è troppo lunga o non pertinente:

1. **Clicca l'icona Stop** ⏹️ (appare durante lo streaming)
2. La generazione si interrompe immediatamente
3. Puoi fare una nuova domanda

### Cancellare la Cronologia

Per iniziare una nuova conversazione:

1. **Clicca "Cancella chat"** 🗑️ in alto a destra
2. **Conferma** l'operazione
3. La cronologia viene eliminata

---

## Interpretare i Risultati

### Fonti e Score di Rilevanza

Ogni risposta della chat mostra le **fonti** utilizzate:

```
┌───────────────────────────────────────────────────────┐
│ Fonti (3 documenti, 8 sezioni usate):                 │
│                                                        │
│ 📄 Manuale_Barriere_Vapore.pdf (87%) ×4              │
│ 📄 Scheda_Tecnica_Derbi.pdf (72%) ×3                 │
│ 📄 Preventivo_Leonardo.pdf (68%) ×1                   │
└───────────────────────────────────────────────────────┘
```

#### Interpretazione

**Manuale_Barriere_Vapore.pdf (87%) ×4:**
- **Nome documento**: Fonte dell'informazione
- **87%**: Score di rilevanza (quanto è pertinente)
- **×4**: Numero di sezioni usate da questo documento

**Cosa significano gli score?**
- **80-100%**: Fonte primaria, informazione molto rilevante
- **65-79%**: Fonte secondaria, informazione di supporto
- **< 65%**: Fonte marginale (filtrata automaticamente)

### Affidabilità delle Risposte

#### ✅ Risposta Affidabile

```
Fonti: 2-4 documenti con score 75-90%
Sezioni: 8-15 sezioni usate
Contenuto: Risposta dettagliata con dati specifici
```

#### ⚠️ Risposta da Verificare

```
Fonti: 1 documento con score 60-70%
Sezioni: 1-3 sezioni usate
Contenuto: Risposta generica o incompleta
```

#### ❌ Nessun Risultato

Se il sistema risponde **"Non ho trovato informazioni"**:
- L'argomento non è presente nei documenti caricati
- Prova a riformulare la domanda
- Verifica di aver caricato i documenti corretti

---

## Impostazioni

### Impostazioni Chat

Nella sezione Chat puoi configurare:

#### 🤖 Modello AI

- **gemini-2.5-flash**: Veloce, ottimo per uso quotidiano (consigliato)
- **gemini-2.5-pro**: Più lento ma più accurato per query complesse

#### 📡 Streaming

- **Attivo** (default): Vedi la risposta in tempo reale mentre viene generata
- **Disattivo**: Vedi la risposta completa solo alla fine

#### 📚 Visualizzazione Fonti

- **Attivo** (default): Mostra le fonti sotto ogni risposta
- **Disattivo**: Nasconde le fonti (risposta più pulita)

### Come Modificare le Impostazioni

1. **Clicca l'icona ingranaggio** ⚙️ in alto a destra nella Chat
2. **Seleziona le opzioni** desiderate
3. Le modifiche sono applicate immediatamente

---

## Best Practices

### 📝 Formulare Domande Efficaci

#### Principi Generali

1. **Sii specifico**: "Costo barriere vapore 100mq" invece di "quanto costa?"
2. **Usa linguaggio naturale**: "Come si installa?" invece di "installazione procedure"
3. **Fornisci contesto**: "Nel preventivo Leonardo, quali sono i costi?"
4. **Una domanda alla volta**: Evita domande multiple nella stessa frase

#### Template Utili

**Per informazioni tecniche:**
```
"Quali sono le caratteristiche di [prodotto/materiale]?"
"Come funziona [processo/sistema]?"
"Qual è la composizione di [materiale]?"
```

**Per informazioni economiche:**
```
"Quanto costa [prodotto/servizio] per [unità di misura]?"
"Confronta i prezzi tra [opzione A] e [opzione B]"
```

**Per procedure:**
```
"Come si installa [prodotto]?"
"Quali sono i passaggi per [processo]?"
"Quali strumenti servono per [operazione]?"
```

### 📁 Organizzare i Documenti

#### Nomenclatura File

✅ **Buone pratiche:**
```
Manuale_Barriere_Vapore_Derbi_2025.pdf
Preventivo_Centro_Commerciale_Leonardo_Gen2025.pdf
Scheda_Tecnica_Isolante_XPS_200mm.pdf
```

❌ **Evita:**
```
doc1.pdf
prev.pdf
scheda.pdf
```

#### Tipologie di Documenti

Organizza per categoria:
- **Manuali tecnici**: Specifiche dettagliate, istruzioni
- **Schede prodotto**: Caratteristiche, certificazioni
- **Preventivi**: Costi, materiali, tempi
- **Progetti**: Disegni, planimetrie
- **Normative**: Leggi, regolamenti, standard

### 🎯 Ottimizzare i Risultati

#### Se i risultati sono poco rilevanti:

1. **Riformula la domanda** con parole diverse
2. **Aggiungi contesto**: Specifica il documento o il progetto
3. **Verifica i documenti**: Assicurati che contengano l'informazione cercata
4. **Carica documenti aggiuntivi** sull'argomento

#### Se i risultati sono troppi:

1. **Sii più specifico** nella domanda
2. **Indica il documento**: "Nel manuale X, ..."
3. **Usa filtri temporali**: "Nel preventivo del 2025, ..."

---

## Risoluzione Problemi

### Problemi Comuni e Soluzioni

#### 🚫 "Nessun documento attivo trovato"

**Causa**: Non hai documenti caricati o sono in elaborazione

**Soluzione:**
1. Vai alla sezione "Documenti"
2. Verifica che ci siano documenti con stato `ACTIVE`
3. Se sono in `PROCESSING`, attendi 30-60 secondi
4. Se sono `FAILED`, ricarica il documento

---

#### ⏸️ La risposta si interrompe improvvisamente

**Causa**: Timeout o errore di rete

**Soluzione:**
1. Verifica la connessione internet
2. Ricarica la pagina
3. Riprova la domanda
4. Se persiste, contatta l'amministratore

---

#### 🔄 "Troppe richieste. Riprova tra un minuto"

**Causa**: Limite di richieste raggiunto (protezione anti-spam)

**Soluzione:**
1. Attendi 60 secondi
2. Riprova la richiesta
3. Evita di inviare troppe domande consecutive

---

#### 📄 Documento caricato ma non trovato in ricerca

**Causa**: Il documento è in elaborazione o il contenuto non matcha la query

**Soluzione:**
1. Verifica stato documento = `ACTIVE`
2. Prova query più generiche
3. Controlla che il documento contenga testo (non solo immagini)
4. Se è una scansione, applica OCR prima di caricare

---

#### 🎯 Score di rilevanza troppo bassi (< 65%)

**Causa**: Documenti poco pertinenti o query troppo generica

**Soluzione:**
1. Carica documenti più specifici sull'argomento
2. Riformula la domanda con termini presenti nei documenti
3. Verifica che i documenti siano nel formato corretto
4. Usa nomi file descrittivi durante l'upload

---

#### 💬 La chat non risponde

**Causa**: Errore del servizio AI o connessione

**Soluzione:**
1. Verifica che ci siano documenti attivi
2. Controlla la connessione internet
3. Ricarica la pagina (F5)
4. Cancella la cache del browser
5. Prova con un browser diverso

---

#### 🔐 Errore 500 - Internal Server Error

**Causa**: Errore del server backend

**Soluzione:**
1. Ricarica la pagina
2. Riprova dopo 1 minuto
3. Contatta l'amministratore se persiste

---

### Quando Contattare il Supporto

Contatta l'amministratore di sistema se:

- ❌ Il sistema non carica completamente
- ❌ I documenti restano in stato `PROCESSING` per più di 5 minuti
- ❌ Ricevi errori 500 ripetuti
- ❌ La chat non funziona mai
- ❌ I documenti non vengono trovati in ricerca nonostante siano `ACTIVE`

**Informazioni da fornire:**
- URL utilizzato
- Browser e versione
- Screenshot dell'errore
- Passi per riprodurre il problema
- Orario dell'errore

---

## FAQ

### Domande Generali

**Q: Quanti documenti posso caricare?**  
A: Non c'è un limite fisso, ma consigliamo max 50-100 documenti per performance ottimali.

**Q: I miei documenti sono sicuri?**  
A: I documenti sono archiviati nel sistema Google File Search con crittografia. Consulta l'amministratore per le policy aziendali specifiche.

**Q: Posso cercare in documenti in altre lingue?**  
A: Il sistema supporta principalmente l'italiano. Documenti in inglese funzionano ma con prestazioni ridotte.

**Q: Quanto tempo serve per elaborare un documento?**  
A: Tipicamente 30-60 secondi per documenti di 10-50 pagine. Documenti più grandi richiedono più tempo.

---

### Ricerca e Chat

**Q: Perché non trovo informazioni che so essere nei documenti?**  
A: Possibili cause:
- Usa termini diversi da quelli nei documenti (es. "BV" vs "barriera vapore")
- Il documento è una scansione non leggibile
- L'informazione è in immagini, non in testo

**Q: Posso fare domande su più documenti contemporaneamente?**  
A: Sì! Il sistema cerca automaticamente in tutti i documenti attivi e integra le informazioni.

**Q: Le risposte sono sempre accurate?**  
A: L'AI genera risposte basate sui documenti caricati. Verifica sempre le fonti citate e consulta l'originale per informazioni critiche.

**Q: Posso esportare le risposte della chat?**  
A: Attualmente no. Puoi copiare manualmente il testo. Feature in sviluppo.

---

### Documenti

**Q: Posso modificare un documento dopo averlo caricato?**  
A: No. Devi eliminare il documento e ricaricare la versione aggiornata.

**Q: Posso caricare documenti ZIP o RAR?**  
A: No. Devi estrarre i file e caricarli singolarmente.

**Q: I metadati dei documenti (autore, data) vengono conservati?**  
A: Attualmente no. Solo il nome file e il contenuto testuale vengono indicizzati.

---

### Performance

**Q: Perché la risposta è lenta?**  
A: Possibili cause:
- Modello AI `gemini-2.5-pro` (più lento ma più accurato)
- Molti documenti caricati
- Connessione internet lenta
- Server sovraccarico

**Q: Come velocizzare le risposte?**  
A: 
- Usa modello `gemini-2.5-flash` (default)
- Fai domande specifiche
- Riduci il numero di documenti caricati
- Usa streaming attivo

---

### Limiti e Restrizioni

**Q: C'è un limite al numero di domande?**  
A: Sì, 30 richieste per minuto per utente (protezione anti-spam).

**Q: Quanto è lungo il contesto mantenuto nella chat?**  
A: Le ultime 2 domande dell'utente (non le risposte dell'AI).

**Q: Posso condividere un link alla chat?**  
A: No. Le conversazioni non sono condivisibili. Feature in sviluppo.

---

## Glossario

**AI (Intelligenza Artificiale)**: Software che simula l'intelligenza umana per comprendere testi e generare risposte.

**Chunk**: Sezione di un documento (circa 300-400 parole) usata per la ricerca.

**Embedding**: Rappresentazione numerica del significato di un testo usata per la ricerca semantica.

**Score di Rilevanza**: Percentuale (0-100%) che indica quanto un chunk è pertinente alla domanda.

**Streaming**: Modalità di ricezione della risposta in tempo reale, parola per parola.

**Token**: Unità di testo (circa 0.75 parole in italiano) usata per calcolare i limiti.

**Query**: Domanda o ricerca inserita dall'utente.

**RAG (Retrieval-Augmented Generation)**: Tecnica AI che combina ricerca nei documenti e generazione di risposte.

---

## Supporto

### Contatti

**Amministratore di Sistema:**
- Email: [da definire]
- Telefono: [da definire]

**Documentazione Tecnica:**
- `DEVELOPER_GUIDE.md` (per sviluppatori)
- `TROUBLESHOOTING.md` (per amministratori)

### Feedback

Hai suggerimenti per migliorare il sistema? Contatta l'amministratore!

---

**Versione Documento**: 1.0  
**Data**: Novembre 2025  
**Autore**: Sistema AI  
**Ultimo Aggiornamento**: 12 Novembre 2025
