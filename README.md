```
  ███████╗██╗   ██╗███╗   ██╗ █████╗ ██████╗ ███████╗███████╗
  ██╔════╝╚██╗ ██╔╝████╗  ██║██╔══██╗██╔══██╗██╔════╝██╔════╝
  ███████╗ ╚████╔╝ ██╔██╗ ██║███████║██████╔╝███████╗█████╗  
  ╚════██║  ╚██╔╝  ██║╚██╗██║██╔══██║██╔═══╝ ╚════██║██╔══╝  
  ███████║   ██║   ██║ ╚████║██║  ██║██║     ███████║███████╗
  ╚══════╝   ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝     ╚══════╝╚══════╝
                                                              
        🧠 AI Context Augmentation Tool
```

<div align="center">

**Help AI agents work accurately in large codebases**

[![Synapse CI](https://github.com/YuanArchive/synapse-ai-context/actions/workflows/ci.yml/badge.svg)](https://github.com/YuanArchive/synapse-ai-context/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![GitHub stars](https://img.shields.io/github/stars/YuanArchive/synapse-ai-context?style=social)](https://github.com/YuanArchive/synapse-ai-context)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/YuanArchive/synapse-ai-context/pulls)

🇰🇷 [한국어 README](README_KO.md) | 📖 [English Manual](docs/MANUAL_EN.md) | 🤖 [AI Setup Guide](docs/AGENT_BOOTSTRAP_EN.md)

> **"Current AI eats tokens like popcorn after 10k lines of code, so I made this."** — Yuan

> *"I just wrote the prompts. AI did all the hard work."* — Yuan, 2026

</div>

---

> [!WARNING]
> **Use at your own risk.** This tool was built by an AI hallucinating at 3am.
> - **Bugs?** Yes.
> - **Tested?** Barely.
> - **Production Ready?** LOL no.
> - **Does it work?** It definitely works on *my* machine.

---

## 📋 Table of Contents

- [✨ Features](#-features)
- [📦 Installation](#-installation)
- [🚀 Quick Start](#-quick-start)
- [🤖 AI Integration](#-ai-integration)
- [📖 Commands](#-commands)
- [🏗️ Architecture](#️-architecture)
- [🔧 Troubleshooting](#-troubleshooting)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## 🌍 Polyglot Support
We parse everything thrown at us. Powered by **Tree-sitter**.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Go](https://img.shields.io/badge/Go-00ADD8?style=for-the-badge&logo=go&logoColor=white)
![Rust](https://img.shields.io/badge/Rust-000000?style=for-the-badge&logo=rust&logoColor=white)
![C++](https://img.shields.io/badge/C++-00599C?style=for-the-badge&logo=c%2B%2B&logoColor=white)
![Java](https://img.shields.io/badge/Java-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white)

---


## ✨ Features

<table>
<tr>
<td width="50%">

### 🔍 Semantic Search
Find code by **meaning**, not just keywords. Powered by ChromaDB vector embeddings.

</td>
<td width="50%">

### 🕸️ Dependency Graph
Understand **what breaks** when you change something. Built with NetworkX.

</td>
</tr>
<tr>
<td width="50%">

### 📊 Incremental Indexing
Only reindex **changed files**. MD5 hash-based change detection.

</td>
<td width="50%">

### 👁️ File Watcher
**Real-time** auto-indexing as you code. Daemon mode for long sessions.

</td>
</tr>
<tr>
<td width="50%">

### 🧠 Deep Think Mode
**Chain-of-Thought** reasoning for complex bugs via `--think` flag.

</td>
<td width="50%">

### 🗜️ Code Compression
**Skeletonize** code to reduce token usage while preserving structure.

</td>
</tr>
</table>

---

## 🌍 Polyglot Support
We parse everything thrown at us. Powered by **Tree-sitter**.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Go](https://img.shields.io/badge/Go-00ADD8?style=for-the-badge&logo=go&logoColor=white)
![Rust](https://img.shields.io/badge/Rust-000000?style=for-the-badge&logo=rust&logoColor=white)
![C++](https://img.shields.io/badge/C++-00599C?style=for-the-badge&logo=c%2B%2B&logoColor=white)
![Java](https://img.shields.io/badge/Java-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white)

---

## 📦 Installation

### Option 1: From GitHub (Recommended)
```bash
pip install git+https://github.com/YuanArchive/synapse-ai-context.git
```

### Option 2: Development Mode
```bash
git clone https://github.com/YuanArchive/synapse-ai-context.git
cd synapse-ai-context
pip install -e .
```

### Requirements
- **Python 3.12+** (Recommended: 3.12.x)
- **C/C++ Compiler**: Required for `tree-sitter` compilation on some systems.
- Dependencies auto-installed: `chromadb`, `networkx`, `tree-sitter`, `watchdog`
- **System Spec:** 8GB+ RAM required (16GB recommended for smooth ChromaDB/ML operations)

> [!TIP]
> **Windows Users**: If the `synapse` command fails with a `Fatal error in launcher`, run all commands using **`python -m synapse`** instead. (e.g., `python -m synapse init`)

### 🛡️ Recommended: Using Virtual Environment

To avoid dependency conflicts with other projects, it is highly recommended to use a virtual environment.

#### Windows
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install git+https://github.com/YuanArchive/synapse-ai-context.git
```

#### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install git+https://github.com/YuanArchive/synapse-ai-context.git
```

---

## 🚀 Quick Start

### 0️⃣ Verify Installation
After installation, check if Synapse is correctly installed:
```bash
synapse --help
```
If you see the command list, you are good to go!
(On Windows, if this fails, use `python -m synapse --help` instead.)

### 1️⃣ Initialize
```bash
cd your-project
python -m synapse init
```

### 2️⃣ Analyze
```bash
synapse analyze .           # Incremental (fast)
synapse analyze . --full    # Full reindex
synapse analyze . --verbose # Debug mode
```

### 3️⃣ Search
```bash
synapse search "login handler"
synapse search "auth" --hybrid  # Vector + Graph
```

### 4️⃣ Check Dependencies
```bash
synapse graph src/auth.py
```

### 5️⃣ Start Watcher (Optional)
```bash
synapse watch start --daemon
```

<details>
<summary>📂 <b>Created Directory Structure</b></summary>

```
your-project/
├── .synapse/              # Index database
│   ├── db/                # ChromaDB vectors
│   ├── dependency_graph.gml
│   ├── file_hashes.json
│   └── INTELLIGENCE.md    # Auto-generated architecture doc
├── .agent/          
│   ├── AI_RULES_EN.md     # AI agent rules (English)
│   └── AI_RULES_KO.md     # AI agent rules (Korean)
└── docs/
    ├── SYNAPSE_MANUAL_KO.md
    └── AGENT_BOOTSTRAP.md
```

</details>

---

## 🤖 AI Integration

### Quick Setup for AI Assistants

Simply tag the bootstrap file in your prompt:

```
@docs/AGENT_BOOTSTRAP_EN.md Set up this project for Synapse
```

The AI will automatically run all setup commands!

### Prime Directives (AI Must Follow)

| Rule | Command |
|------|---------|
| 🔍 **Search Before Strike** | `synapse search <query>` before modifying |
| 🕸️ **Check the Graph** | `synapse graph <file>` before refactoring |
| 🧠 **Deep Think on Failure** | `synapse ask "<error>" --think` when stuck |

### Global Rules Setup

```bash
# Antigravity / Gemini
cp AI_RULES_EN.md ~/.gemini/GEMINI.md

# Cursor
cp AI_RULES_EN.md your-project/.cursorrules
```

---

## 📖 Commands

| Command | Description |
|---------|-------------|
| `python -m synapse init` | Initialize Synapse in a project |
| `python -m synapse analyze .` | Incremental analysis |
| `python -m synapse analyze . --full` | Full reindex |
| `python -m synapse analyze . --verbose` | Debug logging |
| `python -m synapse search "<query>"` | Semantic search |
| `python -m synapse search "<query>" --hybrid` | Vector + Graph search |
| `python -m synapse graph <file>` | Show dependencies |
| `python -m synapse ask "<question>" --think` | Deep reasoning |
| `python -m synapse context <file>` | Hierarchical context |
| `python -m synapse skeleton <file>` | Code skeletonization |
| `python -m synapse watch start` | Start file watcher |
| `python -m synapse watch start --daemon` | Background watcher |
| `python -m synapse watch status` | Check watcher status |
| `python -m synapse watch stop` | Stop watcher |

---

## 🏗️ Architecture

```
synapse/
├── src/synapse/
│   ├── cli.py              # CLI commands (Typer)
│   ├── analyzer.py         # Project analysis engine
│   ├── vector_store.py     # ChromaDB integration
│   ├── graph.py            # Dependency graph (NetworkX)
│   ├── parser.py           # Tree-sitter code parsing
│   ├── watcher.py          # File watcher (watchdog)
│   ├── hybrid_search.py    # Vector + Graph search
│   ├── context_manager.py  # Hierarchical context
│   ├── compressor.py       # Code skeletonization
│   ├── exceptions.py       # Custom exceptions
│   └── logger.py           # Logging system
├── docs/                   # Documentation
└── tests/                  # Test suite
```

---

## 🔧 Troubleshooting

<details>
<summary><b>Python 3.14+ Compatibility Error (ConfigError)</b></summary>

This occurs because Pydantic v1 (a dependency of ChromaDB) is not compatible with Python 3.14.

**Solution:**
We strongly recommend using **Python 3.12**.
1. Install Python 3.12.
2. Create venv: `py -3.12 -m venv .venv`
3. Reinstall: `python -m pip install git+https://github.com/YuanArchive/synapse-ai-context.git`

</details>

<details>
<summary><b>Microsoft Visual C++ 14.0 or greater is required</b></summary>

The `tree-sitter` compiler may require build tools on Windows.

**Solution:**
Install [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) and check the **"Desktop development with C++"** workload.

</details>

<details>
<summary><b>Fatal error in launcher (Windows)</b></summary>

This error occurs when the `pip` executable is tied to an old or non-existent Python path.

**Solution:**
Use `python -m pip` instead of `pip`:
```bash
python -m pip install git+https://github.com/YuanArchive/synapse-ai-context.git
```

</details>

<details>
<summary><b>ChromaDB Error</b></summary>

```bash
rm -rf .synapse/db
python -m synapse analyze . --full
```

</details>

<details>
<summary><b>Watcher Not Responding</b></summary>

```bash
python -m synapse watch stop
python -m synapse watch start --daemon
```

</details>

<details>
<summary><b>Reset Everything</b></summary>

```bash
rm -rf .synapse
python -m synapse init
python -m synapse analyze . --full
```

</details>

---

## 🤝 Contributing

**PLEASE fix this.** I don't know how to code. I just asked AI to "make it work".

- 🐛 **Found a bug?** The whole thing is probably a bug.
- 💡 **Know how Python works?** Send help.
- 🔧 **PRs Welcome:** Please save me from this codebase.

---

## 📄 License

MIT License — Free for personal and commercial use.

---

<div align="center">

## 🙏 Credits

**Yuan** 🧑‍💻 (Prompt Engineer) + **AI** 🤖 (The One Who Actually Wrote The Code)

> *"I just wrote the prompts, AI did all the hard work"*
> — Every developer in 2026

---

**⭐ Star this repo if you find it useful!**

*Powered by Synapse & Antigravity*

</div>
