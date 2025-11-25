# 📁 Struttura Progetto Riorganizzata

## ✨ Cambiamenti

Il progetto è stato riorganizzato per maggiore chiarezza:

```
GoogleFileSearch/
├── 📖 README.md                 # Documentazione principale (rimasto nella root)
├── ⚙️ .env / .env.example       # Configurazione (rimasti nella root)
├── 📦 requirements.txt          # Dipendenze Python (rimasto nella root)
│
├── 🔧 setup/                    # NUOVA CARTELLA - Setup e avvio
│   ├── setup.bat/sh             # Script installazione
│   ├── start.bat/sh             # Script avvio development
│   ├── start-production.sh      # Script avvio production
│   ├── INSTALL.md               # Guida installazione
│   ├── CHECKLIST.md             # Checklist setup
│   └── README.md                # Indice cartella setup
│
├── 📚 docs/                     # NUOVA CARTELLA - Documentazione tecnica
│   ├── LOGICA_FILTRAGGIO_CHUNKS.md  # Architettura RAG
│   ├── TROUBLESHOOTING.md       # Risoluzione problemi
│   ├── IMPROVEMENTS_LOG.md      # Changelog
│   ├── FIX_ERRORE_*.md          # Fix specifici
│   └── README.md                # Indice documentazione
│
├── backend/                     # Backend Flask (invariato)
│   ├── app.py
│   ├── tests/                   # Test suite
│   └── ...
│
└── frontend/                    # Frontend (invariato)
    ├── static/
    └── templates/
```

## 🚀 Come Usare

### Prima installazione
```bash
# Windows
setup\setup.bat

# Linux/Mac
chmod +x setup/setup.sh
./setup/setup.sh
```

### Avvio server
```bash
# Windows
setup\start.bat

# Linux/Mac
chmod +x setup/start.sh
./setup/start.sh
```

### Documentazione
- **Setup**: Vedi `setup/README.md` e `setup/INSTALL.md`
- **Tecnica**: Vedi `docs/README.md`
- **Test**: Vedi `backend/tests/README.md`

## 📝 Vantaggi

✅ **Root più pulita**: Solo file essenziali (README, .env, requirements.txt)
✅ **Setup organizzato**: Tutti gli script in una cartella dedicata
✅ **Documentazione centralizzata**: Guide tecniche separate
✅ **Riferimenti aggiornati**: Tutti i link nel README puntano ai nuovi percorsi
✅ **Script funzionanti**: Tutti gli script aggiornati per funzionare dalla nuova posizione

## ⚠️ Note Importanti

- Gli script in `setup/` funzionano dalla loro posizione usando `cd` automatico
- Tutti i riferimenti nei file sono stati aggiornati
- La struttura backend/ e frontend/ è rimasta invariata
- I file .env e venv/ rimangono nella root del progetto
