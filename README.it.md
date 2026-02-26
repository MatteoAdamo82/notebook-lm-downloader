# NotebookLM Downloader (NBDL)

Tool CLI per scaricare e archiviare localmente i contenuti dei tuoi notebook da [Google NotebookLM](https://notebooklm.google.com/).

Il progetto permette di selezionare interattivamente un notebook e scaricare:
- **Note**: salvate come file Markdown.
- **Sorgenti**: testo completo estratto (JSON e Markdown).
- **Artefatti**: file audio, quiz e mappe concettuali.

## Prerequisiti

- **Docker** e **Docker Compose** installati.
- Credenziali di accesso a NotebookLM (token/cookie) salvate localmente (il tool utilizza `notebooklm-py` che richiede un'autenticazione pregressa).

## Installazione e Setup

Il progetto utilizza Docker per garantire un ambiente isolato. Segui questi passaggi per configurare l'accesso:

### 1. Autenticazione (Una tantum)
Il tool richiede i cookie di sessione di Google NotebookLM. Esegui questi comandi sul tuo host:

```bash
# Installa la libreria necessaria per il login
pip install git+https://github.com/teng-lin/notebooklm-py.git

# Effettua il login (si aprirà il browser)
notebooklm login
```

Questo creerà il file `~/.notebooklm/storage_state.json` contenente i token di sessione. Verifica la sua esistenza:

```bash
ls -la ~/.notebooklm/storage_state.json
```

### 2. Configurazione Ambiente
Copia il file di esempio e personalizza le variabili nel file `.env`:

```bash
cp .env.example .env
```

### 3. Build e Avvio
Costruisci l'immagine e avvia il container:

```bash
# Build dell'immagine
docker compose build

# Esecuzione del downloader
docker compose run --rm downloader
```

## Configurazione (.env)

Il file `.env` permette di gestire i percorsi senza modificare il codice:

- `HOST_CREDENTIALS_PATH`: Percorso locale dove risiedono i cookie (default: `~/.notebooklm`).
- `OUTPUT_PATH`: Directory dove verranno salvati i download (default: `./output`).
- `TZ`: Timezone per i timestamp dei file (default: `Europe/Rome`).

Esempio contenuto `.env`:
```ini
# Credenziali NotebookLM locali (default: ~/.notebooklm)
HOST_CREDENTIALS_PATH=~/.notebooklm

# Cartella di output per i file scaricati (default: ./output)
OUTPUT_PATH=./output

# Timezone (default: Europe/Rome)
TZ=Europe/Rome
```

## Utilizzo

Una volta avviato con `docker compose run --rm downloader`, il tool è interattivo:
1. Visualizzare la lista dei notebook disponibili.
2. Selezionare il notebook desiderato (tramite numero o nome).
3. Attendere il completamento del download.

## Esempio di output

```text
                                  Your Notebooks                                       
┏━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━┓    
┃ #    ┃ Title                                             ┃ Sources ┃ Created    ┃    
┡━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━┩    
│ 1    │ Advanced Coding Agents Strategy                   │       0 │ 2026-02-25 │    
├──────┼───────────────────────────────────────────────────┼─────────┼────────────┤    
│ 2    │ Developer Lifecycle Automation                    │      12 │ 2026-02-25 │    
├──────┼───────────────────────────────────────────────────┼─────────┼────────────┤    
│ 3    │ AI Video Tools Research                           │       5 │ 2026-02-22 │    
└──────┴───────────────────────────────────────────────────┴─────────┴────────────┘    
                                                                                       
Select notebook (number or name, Tab to complete): 2                                   
                                                                                       
Selected notebook: Developer Lifecycle Automation (id: 823f1a55-...)                                                  
                                                                                       
→ Notes                                                                                
  Downloading 5 notes...                                                              
    ✓ strategy_for_effective_ai_agents.md                     
    ✓ secure_deployment_guide_vps.md                            
    ✓ proactive_monitoring_integration.md                
    ✓ token_economics_and_cost_management.md         
    ✓ prompt_injection_defense_guide.md
    ...                                  
                                                                                       
→ Sources                                                                              
  Downloading fulltext of 5 sources...                                                 
    ✓ introduction_to_autonomous_agents.md / .json (8,675 chars)                                  
    ✓ api_integrations_overview.md / .json (3,497 chars)                                   
    ✓ security_best_practices.md / .json (3,509 chars)                      
    ✓ scaling_ai_infrastructure.md / .json (32,224 chars)         
    ✓ future_of_coding_assistants.md / .json (4,096 chars)                                       
    ...
                                                                                       
→ Artifacts                                                                            
  Downloading 2 artifacts...                                                           
    ✓ podcast_deep_dive_into_automation.mp3                                      
    ✓ quiz_devops_best_practices.json
```

## Output

I file scaricati vengono salvati nella cartella `output/` creata nella root del progetto, organizzati per notebook e data di esecuzione:

```
output/
└── nome-notebook_YYYYMMDD_HHMMSS/
    ├── notebook.json       # Metadati del notebook
    ├── notes/              # Note in formato Markdown
    ├── sources/            # Sorgenti originali (JSON + Markdown)
    └── artifacts/          # Audio, Quiz, Mappe concettuali
```

## Architettura

Il progetto segue i principi di containerizzazione ("Tutto in Docker").
Attualmente è strutturato come script singolo (`nbdl.py`), ma è predisposto per evoluzioni future verso un'architettura più modulare (Interface-based, DI) per progetti più complessi.

## Sviluppo Locale (Debug)

Per esigenze di debug o sviluppo rapido senza container, è possibile eseguire l'applicazione in un virtual environment:

1.  **Crea l'ambiente virtuale**:
    ```bash
    python3 -m venv venv
    ```

2.  **Attiva l'ambiente**:
    ```bash
    source venv/bin/activate
    ```

3.  **Installa le dipendenze**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Esegui l'applicazione**:
    ```bash
    # Assicurati di aver configurato il file .env
    python3 nbdl.py
    ```
