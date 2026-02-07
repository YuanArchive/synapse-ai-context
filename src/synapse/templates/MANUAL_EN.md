# 🧠 Synapse User Manual

> **AI Context Augmentation Tool** — Help AI agents work accurately in large codebases

---

## 📋 Table of Contents

1. [Installation](#1-installation)
2. [Project Initialization](#2-project-initialization)
3. [Code Analysis](#3-code-analysis)
4. [Search](#4-search)
5. [Dependency Graph](#5-dependency-graph)
6. [File Watcher](#6-file-watcher)
7. [AI Agent Integration](#7-ai-agent-integration)
8. [Error Handling Protocol](#8-error-handling-protocol)
9. [Command Reference](#9-command-reference)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Installation

### Method A: pip install (Recommended)
```bash
pip install git+https://github.com/YuanArchive/synapse-ai-context.git
```

### Method B: Development mode
```bash
git clone https://github.com/YuanArchive/synapse-ai-context.git
pip install -e ./synapse-ai-context
```

### Requirements
- **Python 3.12** (Strongly Recommended)
  - *Note: Python 3.14+ is currently incompatible due to dependency issues.*
- **C/C++ Compiler**: May be required for `tree-sitter` compilation.
- **Virtual Environment**: Highly recommended to avoid dependency conflicts.

### Installation & Verification
1. Create and activate a virtual environment (`venv`).
2. Install the package:
   ```bash
   pip install git+https://github.com/YuanArchive/synapse-ai-context.git
   ```
3. Verify installation:
   ```bash
   python -m synapse --help
   ```

---

## 2. Project Initialization

```bash
cd your-project
python -m synapse init
```

**Created structure:**
```
your-project/
├── .synapse/              # Synapse data
│   ├── db/                # ChromaDB vector store
│   ├── dependency_graph.gml
│   ├── file_hashes.json
│   ├── synapse_YYYYMMDD.log  # Log files
│   └── INTELLIGENCE.md
├── .context/              # Context storage
├└── .agent/          # AI agent rules
    ├── AI_RULES_KO.md
    └── AI_RULES_EN.md
└── docs/
    ├── SYNAPSE_MANUAL_KO.md
    └── AGENT_BOOTSTRAP.md
```

---

## 3. Code Analysis

### Incremental Analysis (Default, Fast)
```bash
python -m synapse analyze .
```
- Only reindexes changed files
- MD5 hash-based change detection

### Full Reanalysis
```bash
python -m synapse analyze . --full
```

### Verbose Mode (Debugging)
```bash
python -m synapse analyze . --verbose
```
- Outputs detailed debug information
- Saves logs to `.synapse/synapse_YYYYMMDD.log`

### Output Example
```
## Synapse Analysis (Incremental): `.`
- **Changed Files:** 3
- **Unchanged Files:** 45
- **Graph Nodes:** 200
INFO: Analysis complete: 3 files processed
```

---

## 4. Search

### Semantic Search
```bash
python -m synapse search "login handler"
```

### Hybrid Search (Vector + Graph)
```bash
python -m synapse search "auth" --hybrid
```

### Compressed Results
```bash
python -m synapse search "query" --compress
```

---

## 5. Dependency Graph

```bash
python -m synapse graph src/services/auth.py
```

**Output:**
```
### 📤 Dependencies (Calls)
- Calls `validate_token` in `src/utils/jwt.py`

### 📥 Dependents (Called By)
- Called by `src/api/routes.py` (via `login`)
```

---

## 6. File Watcher

### Foreground Mode
```bash
python -m synapse watch start
# Ctrl+C to stop
```

### Background Daemon
```bash
python -m synapse watch start --daemon
```

### Check Status
```bash
python -m synapse watch status
```

### Stop
```bash
python -m synapse watch stop
```

### How It Works
1. Detects file changes (watchdog)
2. 2-second debounce
3. Auto incremental indexing
4. AI always has latest data

---

## 7. AI Agent Integration

### Rules File Location
```
project/.agent/AI_RULES_EN.md (or _KO.md)
```

### AI Agent Workflow

#### Before Starting Work
```bash
python -m synapse analyze .                  # Update index
python -m synapse watch start --daemon       # Or start watcher
```

#### Before Modifying Code
```bash
python -m synapse search "feature to modify"  # Search code
python -m synapse graph target_file.py       # Check impact
```

#### On Error
```bash
python -m synapse ask "error message" --think  # CoT reasoning
```

---

## 8. Error Handling Protocol

Steps AI follows when errors occur:

### Step 1: Collect Verbose Logs
```bash
python -m synapse analyze . --verbose
```

### Step 2: Check Log Files
```bash
cat .synapse/synapse_*.log | tail -50
```

### Step 3: Analyze Error
```bash
python -m synapse ask "<error message>" --think
```

### Step 4: Error Type Reference
| Error | Action |
|-------|--------|
| `ParserError` | Check file syntax |
| `IndexingError` | Run `--full` reindex |
| `GraphError` | Check GML integrity |
| `SearchError` | Modify query |
| `WatcherError` | Restart watcher |

---

## 9. Command Reference

| Command | Description |
|---------|-------------|
| `python -m synapse init` | Initialize project |
| `python -m synapse analyze .` | Incremental analysis |
| `python -m synapse analyze . --full` | Full reindex |
| `python -m synapse analyze . --verbose` | Verbose logging |
| `python -m synapse search "<query>"` | Semantic search |
| `python -m synapse search "<query>" --hybrid` | Hybrid search |
| `python -m synapse graph <file>` | Check dependencies |
| `python -m synapse ask "<question>" --think` | Deep reasoning |
| `python -m synapse context <file>` | Hierarchical context |
| `python -m synapse skeleton <file>` | Code skeletonization |
| `python -m synapse watch start` | Start watcher |
| `python -m synapse watch start --daemon` | Background watcher |
| `python -m synapse watch status` | Check status |
| `python -m synapse watch stop` | Stop watcher |

---

## 10. Troubleshooting

### Fatal error in launcher (Windows)
- Use `python -m pip` instead of `pip`.
- Example: `python -m pip install git+https://github.com/YuanArchive/synapse-ai-context.git`

### ChromaDB Error
```bash
rm -rf .synapse/db
python -m synapse analyze . --full
```

### Watcher Not Responding
```bash
python -m synapse watch stop
python -m synapse watch start --daemon
```

### Reset Everything
```bash
rm -rf .synapse
python -m synapse init
python -m synapse analyze . --full
```

### File Encoding Error
- Ensure files are UTF-8 encoded
- Binary files are automatically excluded

## 11. Uninstallation

If you need to remove or reinstall the tool, use the following commands.

### Remove Package
```bash
pip uninstall synapse-tool
```

### Remove Data
To remove generated data and configuration files:
```bash
# Windows
rmdir /s /q .synapse .context .agent

# Mac/Linux
rm -rf .synapse .context .agent
```

---

*Synapse v0.1.0 | *Powered by Synapse & Antigravity*
