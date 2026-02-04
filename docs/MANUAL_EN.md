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
pip install git+https://github.com/YOUR_USERNAME/synapse.git
```

### Method B: Development mode
```bash
git clone https://github.com/YOUR_USERNAME/synapse.git
pip install -e ./synapse
```

### Requirements
- Python 3.12+
- Dependencies auto-installed: `chromadb`, `networkx`, `tree-sitter`, `watchdog`

---

## 2. Project Initialization

```bash
cd your-project
synapse init
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
├── .antigravity/          # AI agent rules
│   └── rules.md
└── docs/
    ├── SYNAPSE_MANUAL_KO.md
    └── AGENT_BOOTSTRAP.md
```

---

## 3. Code Analysis

### Incremental Analysis (Default, Fast)
```bash
synapse analyze .
```
- Only reindexes changed files
- MD5 hash-based change detection

### Full Reanalysis
```bash
synapse analyze . --full
```

### Verbose Mode (Debugging)
```bash
synapse analyze . --verbose
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
synapse search "login handler"
```

### Hybrid Search (Vector + Graph)
```bash
synapse search "auth" --hybrid
```

### Compressed Results
```bash
synapse search "query" --compress
```

---

## 5. Dependency Graph

```bash
synapse graph src/services/auth.py
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
synapse watch start
# Ctrl+C to stop
```

### Background Daemon
```bash
synapse watch start --daemon
```

### Check Status
```bash
synapse watch status
```

### Stop
```bash
synapse watch stop
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
project/.antigravity/rules.md
```

### AI Agent Workflow

#### Before Starting Work
```bash
synapse analyze .                  # Update index
synapse watch start --daemon       # Or start watcher
```

#### Before Modifying Code
```bash
synapse search "feature to modify"  # Search code
synapse graph target_file.py       # Check impact
```

#### On Error
```bash
synapse ask "error message" --think  # CoT reasoning
```

---

## 8. Error Handling Protocol

Steps AI follows when errors occur:

### Step 1: Collect Verbose Logs
```bash
synapse analyze . --verbose
```

### Step 2: Check Log Files
```bash
cat .synapse/synapse_*.log | tail -50
```

### Step 3: Analyze Error
```bash
synapse ask "<error message>" --think
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
| `synapse init` | Initialize project |
| `synapse analyze .` | Incremental analysis |
| `synapse analyze . --full` | Full reindex |
| `synapse analyze . --verbose` | Verbose logging |
| `synapse search "<query>"` | Semantic search |
| `synapse search "<query>" --hybrid` | Hybrid search |
| `synapse graph <file>` | Check dependencies |
| `synapse ask "<question>" --think` | Deep reasoning |
| `synapse context <file>` | Hierarchical context |
| `synapse skeleton <file>` | Code skeletonization |
| `synapse watch start` | Start watcher |
| `synapse watch start --daemon` | Background watcher |
| `synapse watch status` | Check status |
| `synapse watch stop` | Stop watcher |

---

## 10. Troubleshooting

### ChromaDB Error
```bash
rm -rf .synapse/db
synapse analyze . --full
```

### Watcher Not Responding
```bash
synapse watch stop
synapse watch start --daemon
```

### Reset Everything
```bash
rm -rf .synapse
synapse init
synapse analyze . --full
```

### File Encoding Error
- Ensure files are UTF-8 encoded
- Binary files are automatically excluded

---

*Synapse v0.1.0 | *Powered by Synapse & Antigravity*
