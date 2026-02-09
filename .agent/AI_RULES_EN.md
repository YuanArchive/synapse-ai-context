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
| `LauncherError` | Use `python -m synapse ...` on Windows |

---

## 🛠️ Tool Quick Reference

| Goal | Command |
| :--- | :--- |
| **Initialize** | `synapse init` |
| **Analyze (Incremental)** | `synapse analyze .` |
| **Analyze (Parallel)** | `synapse analyze . --workers <N>` (Faster) |
| **Analyze (Full)** | `synapse analyze . --full` |
| **Analyze (Debug)** | `synapse analyze . --verbose` |
| **Search** | `synapse search "<query>"` |
| **Hybrid Search** | `synapse search "<query>" --hybrid` |
| **Check Impact** | `synapse graph <file_path>` |
| **Deep Reasoning** | `synapse ask "<question>" --think` |
| **Start Watcher** | `synapse watch start --daemon` |
| **Watcher Status** | `synapse watch status` |
| **Stop Watcher** | `synapse watch stop` |

## ⚡ Performance Optimization

### GPU Acceleration
Synapse supports **GPU acceleration** for 5~10x faster embedding generation.

**Check GPU availability**:
```bash
# Check PyTorch CUDA
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"

# Check GPU status
nvidia-smi
```

**If GPU is not detected**:
- CPU-only PyTorch installed: Reinstall with CUDA support
- See `docs/PERFORMANCE_TUNING.md` for details

### Environment Variable: SYNAPSE_BATCH_SIZE
Control embedding batch size to optimize GPU memory usage and performance.

**Default**: `12`

**Usage** (PowerShell):
```powershell
# GPU VRAM 12GB (RTX 3080 Ti): batch size 16 recommended
$env:SYNAPSE_BATCH_SIZE = "16"
synapse analyze . --workers 4

# GPU memory insufficient: reduce batch size
$env:SYNAPSE_BATCH_SIZE = "8"
synapse analyze . --workers 2
```

**Recommended Settings**:
| GPU VRAM | Batch Size | Workers | Performance |
|----------|-----------|---------|-------------|
| CPU only | 4~8 | 2~4 | Slow |
| 8GB | 8~12 | 2~4 | Moderate |
| 12GB | 12~16 | 4~6 | **Fast** |
| 16GB+ | 16~32 | 6~8 | Very Fast |

### Parallel Processing
Optimize performance for large codebases by adjusting worker count.

```bash
# 4 workers (recommended)
synapse analyze . --workers 4

# 6 workers (large projects)
synapse analyze . -w 6
```

**Note**: Too many workers may cause GPU memory issues.

### Handling GPU Memory Errors
If `CUDA out of memory` occurs:

1. **Reduce batch size**:
   ```powershell
   $env:SYNAPSE_BATCH_SIZE = "8"
   ```

2. **Reduce worker count**:
   ```bash
   synapse analyze . --workers 2
   ```

3. **Use incremental update** (default) instead of full reindex:
   ```bash
   synapse analyze .  # avoid --full flag
   ```

> [!TIP]
> **Performance**: With GPU acceleration, use `--workers 4` + `SYNAPSE_BATCH_SIZE=16` for optimal performance.
> **Quality**: We now use Jina Embeddings v2 (8k context). Trust the search results!
> **Troubleshooting**: For GPU-related issues, see `docs/PERFORMANCE_TUNING.md`.

---

**By using Synapse, you agree to follow these protocols strictly.**

*Synapse v0.1.0 | MIT License*
