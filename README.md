# NotebookLM Downloader (NBDL)

CLI tool to download and archive your notebook contents locally from [Google NotebookLM](https://notebooklm.google.com/).

The project allows you to interactively select a notebook and download:
- **Notes**: Saved as Markdown files.
- **Sources**: Full extracted text (JSON and Markdown).
- **Artifacts**: Audio files, quizzes, and concept maps.

## Prerequisites

- **Docker** and **Docker Compose** installed.
- NotebookLM access credentials (token/cookies) saved locally (the tool uses `notebooklm-py` which requires prior authentication).

## Installation and Setup

The project uses Docker to ensure an isolated environment. Follow these steps to configure access:

### 1. Authentication (One-time)
The tool requires Google NotebookLM session cookies. Run these commands on your host:

```bash
# Install the library needed for login
pip install git+https://github.com/teng-lin/notebooklm-py.git

# Log in (browser will open)
notebooklm login
```

This will create the `~/.notebooklm/storage_state.json` file containing session tokens. Verify its existence:

```bash
ls -la ~/.notebooklm/storage_state.json
```

### 2. Environment Configuration
Copy the example file and customize the variables in the `.env` file:

```bash
cp .env.example .env
```

### 3. Build and Run
Build the image and start the container:

```bash
# Build the image
docker compose build

# Run the downloader
docker compose run --rm downloader
```

## Configuration (.env)

The `.env` file allows managing paths without modifying the code:

- `HOST_CREDENTIALS_PATH`: Local path where cookies reside (default: `~/.notebooklm`).
- `OUTPUT_PATH`: Directory where downloads will be saved (default: `./output`).
- `TZ`: Timezone for file timestamps (default: `Europe/Rome`).

Example `.env` content:
```ini
# Local NotebookLM credentials (default: ~/.notebooklm)
HOST_CREDENTIALS_PATH=~/.notebooklm

# Output folder for downloaded files (default: ./output)
OUTPUT_PATH=./output

# Timezone (default: Europe/Rome)
TZ=Europe/Rome
```

## Usage

Once started with `docker compose run --rm downloader`, the tool is interactive:
1. View the list of available notebooks.
2. Select the desired notebook (by number or name).
3. Wait for the download to complete.

### Example Output

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

Downloaded files are saved in the `output/` folder created in the project root, organized by notebook and execution date:

```
output/
└── notebook-name_YYYYMMDD_HHMMSS/
    ├── notebook.json       # Notebook metadata
    ├── notes/              # Notes in Markdown format
    ├── sources/            # Original sources (JSON + Markdown)
    └── artifacts/          # Audio, Quiz, Concept Maps
```

## Architecture

The project follows containerization principles ("Everything in Docker").
Currently structured as a single script (`nbdl.py`), but designed for future evolution towards a more modular architecture (Interface-based, DI) for more complex projects.

## Local Development (Debug)

For debug or rapid development needs without containers, you can run the application in a virtual environment:

1.  **Create the virtual environment**:
    ```bash
    python3 -m venv venv
    ```

2.  **Activate the environment**:
    ```bash
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application**:
    ```bash
    # Ensure you have configured the .env file
    python3 nbdl.py
    ```
