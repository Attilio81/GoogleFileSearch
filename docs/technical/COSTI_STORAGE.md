# Costi Storage e API - Google File Search

## 📊 Panoramica Costi

Il sistema utilizza **Google Gemini File API** per storage, embedding e retrieval dei documenti. Ecco i costi aggiornati (Novembre 2025).

---

## 💰 Prezzi Google File Search API

### Storage Documenti

| Metrica | Quota Gratuita | Costo oltre soglia |
|---------|----------------|-------------------|
| **Storage totale** | 20 GB | **$0.03/GB al giorno** |
| **Numero file** | Illimitato | Gratuito |
| **Retention** | Automatica (48h inattività) | N/A |

> **Nota**: Google elimina automaticamente i file non acceduti per 48h per ottimizzare i costi.

---

### Generazione Embedding

| Operazione | Quota Gratuita | Costo oltre soglia |
|------------|----------------|-------------------|
| **Embedding (input)** | 15.000 documenti/giorno | **$0.10 per 1M caratteri** |
| **Modello**: `text-embedding-004` | - | - |

> **Stima**: 1 documento PDF (50 pagine, ~25.000 caratteri) = ~$0.0025

---

### Generazione Risposte

| Modello | Input (per 1M token) | Output (per 1M token) | Context Window |
|---------|---------------------|----------------------|----------------|
| **gemini-2.5-flash** | $0.075 | $0.30 | 1M token |
| **gemini-2.5-pro** | $1.25 | $5.00 | 2M token |

> **Consiglio**: Usa `gemini-2.5-flash` (default) per il 95% delle query.

---

### Query/Retrieval

| Operazione | Quota Gratuita | Costo oltre soglia |
|------------|----------------|-------------------|
| **Query API** (retrieval chunks) | 1.500 richieste/giorno | **$0.50 per 1.000 richieste** |
| **Chunks restituiti** | Illimitati | Incluso |

---

## 🧮 Simulazioni di Costo

### Scenario 1: Studio Tecnico (10 Utenti, 1.000 Preventivi/Anno)

**Configurazione:**
- 1.000 preventivi/documenti (PDF 20 pagine media)
- 10 utenti attivi
- ~100 query/giorno (10 utenti × 10 query/giorno)
- 90% gemini-flash, 10% gemini-pro

**Costi Mensili:**

| Voce | Calcolo | Costo/mese |
|------|---------|------------|
| Storage (10 GB) | 10 GB × $0.03 × 30 giorni | $9.00 |
| Embedding iniziale | 1.000 doc × 10.000 char × $0.10/1M | $1.00 (una tantum) |
| Query retrieval | (100 × 30) / 1.500 gratis = 1.500 extra × $0.50/1k | $0.75 |
| Generazione flash | 90 query/giorno × 30 giorni × 2.500 token × $0.075/1M | $0.51 |
| Generazione pro | 10 query/giorno × 30 giorni × 2.500 token × $1.25/1M | $0.09 |
| **TOTALE** | - | **~$11/mese** |

**Costo annuale stimato**: ~**$130/anno** (primo anno include embedding una tantum)

> **Note:**
> - Preventivo medio: 20 pagine = ~10.000 caratteri
> - 10 query/utente/giorno = uso moderato (2-3 consulenze/giorno)
> - Storage 10 GB = 1.000 PDF × 10 KB/file medio

---

### Scenario 1B: Piccola Azienda (10 Utenti, Uso Generico)

**Configurazione:**
- 50 documenti (PDF 30 pagine media)
- 200 query/giorno
- 80% flash, 20% pro

**Costi Mensili:**

| Voce | Calcolo | Costo/mese |
|------|---------|------------|
| Storage (5 GB) | 5 GB × $0.03 × 30 giorni | $4.50 |
| Embedding iniziale | 50 doc × 15.000 char × $0.10/1M | $0.08 (una tantum) |
| Query retrieval | (200 × 30) / 1.500 gratis = 4.500 extra × $0.50/1k | $2.25 |
| Generazione flash | 160 query × 2.000 token × $0.075/1M | $0.02 |
| Generazione pro | 40 query × 2.000 token × $1.25/1M | $0.10 |
| **TOTALE** | - | **~$7/mese** |

---

### Scenario 2: Media Azienda (50 Utenti)

**Configurazione:**
- 500 documenti (PDF 40 pagine media)
- 1.500 query/giorno
- 90% flash, 10% pro

**Costi Mensili:**

| Voce | Calcolo | Costo/mese |
|------|---------|------------|
| Storage (50 GB) | 50 GB × $0.03 × 30 giorni | $45.00 |
| Embedding iniziale | 500 doc × 20.000 char × $0.10/1M | $1.00 (una tantum) |
| Query retrieval | (1.500 × 30) / 1.500 gratis = 43.500 × $0.50/1k | $21.75 |
| Generazione flash | 1.350 query × 3.000 token × $0.075/1M | $0.30 |
| Generazione pro | 150 query × 3.000 token × $1.25/1M | $0.56 |
| **TOTALE** | - | **~$69/mese** |

---

### Scenario 3: Grande Azienda (200 Utenti)

**Configurazione:**
- 2.000 documenti (PDF 50 pagine media)
- 5.000 query/giorno
- 95% flash, 5% pro

**Costi Mensili:**

| Voce | Calcolo | Costo/mese |
|------|---------|------------|
| Storage (200 GB) | 200 GB × $0.03 × 30 giorni | $180.00 |
| Embedding iniziale | 2.000 doc × 25.000 char × $0.10/1M | $5.00 (una tantum) |
| Query retrieval | (5.000 × 30) / 1.500 gratis = 148.500 × $0.50/1k | $74.25 |
| Generazione flash | 4.750 query × 4.000 token × $0.075/1M | $1.43 |
| Generazione pro | 250 query × 4.000 token × $1.25/1M | $1.25 |
| **TOTALE** | - | **~$262/mese** |

---

## 📉 Ottimizzazione Costi

### 1. **Ridurre Storage**

✅ **Best Practices:**
- Elimina documenti obsoleti/duplicati
- Comprimi PDF prima dell'upload
- Usa retention automatica (48h inattività)
- Archivia versioni vecchie esternamente

💡 **Risparmio**: Fino al 40% sui costi storage

---

### 2. **Ottimizzare Query**

✅ **Best Practices:**
- Cache locale per query frequenti (implementabile)
- Aggrega domande simili
- Filtra documenti inattivi (evita query su tutto)

💡 **Risparmio**: Fino al 30% sui costi retrieval

---

### 3. **Scelta Modello Generazione**

| Caso d'Uso | Modello Consigliato | Motivo |
|------------|---------------------|---------|
| Query semplici | `gemini-2.5-flash` | 17x più economico |
| Analisi complesse | `gemini-2.5-pro` | Maggiore accuratezza |
| Report lunghi | `gemini-2.5-flash` | Sufficiente per sintesi |

💡 **Risparmio**: Usa flash al 90% → costi generation ridotti del 90%

---

### 4. **Limiti Utente**

✅ **Configurazione `.env`:**
```env
MAX_QUERIES_PER_USER_PER_MINUTE=10
MAX_CHUNKS_FOR_GENERATION=15  # Ridurre a 10 se necessario
MAX_OUTPUT_TOKENS=4096  # Ridurre a 2048 per risposte brevi
```

💡 **Risparmio**: Previene abusi, riduce costi del 20%

---

## 🚨 Soglie di Allerta

Configura avvisi quando:

| Soglia | Azione Consigliata |
|--------|-------------------|
| **Storage > 80% quota** | Rimuovi documenti obsoleti |
| **Query > 1.000/giorno** | Verifica attività anomale |
| **Costo > $50/mese** | Analizza pattern di utilizzo |
| **Spike improvviso (+200%)** | Controlla bot/automation |

---

## 🔄 Alternative per Ridurre Costi

### Opzione 1: Modello Locale (Privacy + Zero Costi API)

| Componente | Soluzione | Costo |
|------------|----------|-------|
| **Embedding** | `sentence-transformers/all-MiniLM-L6-v2` | Gratis |
| **Vector DB** | ChromaDB / FAISS locale | Gratis |
| **Generation** | Ollama (Qwen 2.5 7B) | Gratis |
| **Hardware** | Server con RTX 3060 (8GB) | ~$600 hardware |

**Pro:**
- ✅ Zero costi API mensili
- ✅ Privacy totale (dati mai in cloud)
- ✅ Latenza inferiore (rete locale)

**Contro:**
- ❌ Investimento hardware iniziale
- ❌ Qualità inferiore rispetto a Gemini Pro
- ❌ Manutenzione server

---

### Opzione 2: Modello Ibrido

**Storage + Embedding**: Google (sfrutta quota gratuita)  
**Generation**: DeepSeek-V3 ($0.27/1M token)

**Risparmio generation**: 72% rispetto a Gemini Flash

---

## 📊 Monitoraggio Costi

### Dashboard Google Cloud Console

1. **Vai a**: https://console.cloud.google.com/billing
2. **Seleziona progetto**: `GoogleFileSearch`
3. **Monitora**:
   - Storage giornaliero
   - Chiamate API
   - Token consumati
4. **Imposta Budget Alert**: Es. $100/mese

### Log Backend

Il sistema logga automaticamente:
```
[INFO] Query su 7 documenti attivi, 4 chunks per documento
[INFO] Totale chunks aggregati: 21, token stimati: ~8.400
```

Usa questi log per stimare i costi giornalieri.

---

## 🎯 Raccomandazioni Finali

### Per Studi Tecnici / Piccole Aziende (< 50 utenti)
- ✅ Usa Google File Search (costi bassi, setup zero)
- ✅ Mantieni < 20 GB storage
- ✅ Flash al 90-95%
- **Costo atteso**: $10-20/mese
- **Con 1.000 preventivi/anno**: ~$11-15/mese ($130-180/anno)

### Per Medie Aziende (50-200 utenti)
- ✅ Google File Search con ottimizzazioni
- ✅ Cache query frequenti (custom)
- ✅ Monitora storage settimanalmente
- **Costo atteso**: $50-100/mese

### Per Grandi Aziende (> 200 utenti)
- ⚠️ Valuta soluzione ibrida o locale
- ⚠️ Costi > $200/mese → ROI modello locale migliore
- ✅ Implementa cache avanzata + CDN
- **Costo atteso**: $150-300/mese (cloud) vs $600 una tantum (locale)

---

## 📞 Supporto Costi

**Domande frequenti:**

**Q: Come riduco i costi se supero il budget?**  
A: 1) Elimina documenti inutilizzati, 2) Usa solo gemini-flash, 3) Riduci MAX_CHUNKS_FOR_GENERATION a 10

**Q: Posso impostare un limite di spesa?**  
A: Sì, in Google Cloud Console → Billing → Budget & Alerts

**Q: Quanto costa migrare a soluzione locale?**  
A: Hardware: ~$600-1.500 + tempo setup: 2-3 giorni

---

**Versione Documento**: 1.0  
**Ultimo Aggiornamento**: 12 Novembre 2025  
**Fonte Prezzi**: https://ai.google.dev/pricing  
**Validità**: Prezzi soggetti a variazione (verificare sempre fonte ufficiale)
