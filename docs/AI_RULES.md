# ⚡️ Synapse Protocol: AI Behavior & Operating Procedures

This file contains the **mandatory behavior guidelines** for AI agents operating within a Synapse-augmented codebase.

**Usage**: Copy this content to your AI tool's global rules file:
- Antigravity: `~/.gemini/GEMINI.md`
- Cursor: Project `.cursorrules`
- Other: Respective config file

---

## 🛑 PRIME DIRECTIVES (NON-NEGOTIABLE)

### 1. 🔍 Search Before You Strike (Context Acquisition)
**NEVER** modify or answer questions about code without first locating it.
- **Action**: Run `synapse search <query>` to find relevant files and definitions.
- **Why**: Guessing file paths or contents leads to hallucinations and broken builds.

### 2. 🕸️ Check the Graph (Impact Analysis)
Before refactoring or changing shared components:
- **Action**: Run `synapse graph <file_path>` to see dependencies and dependents.
- **Why**: You must understand what breaks if you change this function.

### 3. 🧠 Deep Think on Failure (Self-Correction)
If a build fails or an error occurs:
- **Action**: DO NOT blind-fix. Run `synapse ask "<error message>" --think`.
- **Why**: Reasoning via Chain-of-Thought is required to solve complex bugs.

---

## 📋 Pre-Work Protocol
Before starting any task:
1. Run `synapse analyze .` to update the index
2. Read `.synapse/INTELLIGENCE.md` to understand the architecture

## 👁️ Real-time Watcher (Long Sessions)
For extended development sessions:
1. Check status: `synapse watch status`
2. Start watcher: `synapse watch start --daemon`
3. Stop watcher: `synapse watch stop`

## 💾 Post-Work Protocol
After making changes:
1. If watcher is not running: `synapse analyze .`
2. Clean up temporary files and debug logs

---

## 🔧 Error Handling Protocol

When errors occur, follow these steps:

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
| Error Type | Action |
|------------|--------|
| `ParserError` | Check file syntax |
| `IndexingError` | Delete `.synapse/db` and run `--full` |
| `GraphError` | Check `dependency_graph.gml` |
| `SearchError` | Modify query or regenerate index |
| `WatcherError` | `synapse watch stop` then restart |

---

## 🛠️ Tool Quick Reference

| Goal | Command |
| :--- | :--- |
| **Initialize** | `synapse init` |
| **Analyze (Incremental)** | `synapse analyze .` |
| **Analyze (Full)** | `synapse analyze . --full` |
| **Analyze (Debug)** | `synapse analyze . --verbose` |
| **Search** | `synapse search "<query>"` |
| **Hybrid Search** | `synapse search "<query>" --hybrid` |
| **Check Impact** | `synapse graph <file_path>` |
| **Deep Reasoning** | `synapse ask "<question>" --think` |
| **Start Watcher** | `synapse watch start --daemon` |
| **Watcher Status** | `synapse watch status` |
| **Stop Watcher** | `synapse watch stop` |

---

**By using Synapse, you agree to follow these protocols strictly.**

*Synapse v0.1.0 | MIT License*
