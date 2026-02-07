# 🚀 Synapse Agent Bootstrap

> **FOR AI AGENTS ONLY** — When AI reads this file, execute the steps below in order.

---

## 🎯 Quick Command (One-Line Setup)

```bash
synapse init && synapse analyze . --full && synapse watch start --daemon
```

---

## 📋 Step-by-Step Setup

### Step 1: Initialize Synapse
```bash
synapse init
```
- Creates `.synapse/`, `.context/`, `.agent/` directories
- Auto-generates `AI_RULES_KO.md`, `AI_RULES_EN.md`

### Step 2: Full Index
```bash
synapse analyze . --full
```
- Parses all code files
- Builds vector index + dependency graph

### Step 3: Start Watcher (Optional)
```bash
synapse watch start --daemon
```
- Background file monitoring
- Auto incremental indexing

### Step 4: Read Architecture
```bash
# Read file
.synapse/INTELLIGENCE.md
```
- Understand project architecture
- Identify core modules and dependencies

---

## ✅ Setup Complete Checklist

After running the commands above, verify:

- [ ] `.synapse/` directory exists
- [ ] `.synapse/dependency_graph.gml` created
- [ ] `synapse watch status` → Running (optional)

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| synapse command not found | `pip install git+https://github.com/YuanArchive/synapse-ai-context.git` |
| ChromaDB error | `rm -rf .synapse/db && synapse analyze . --full` |
| Watcher failure | `synapse watch stop && synapse watch start --daemon` |

---

## 📖 After Setup

After setup complete, AI follows these rules:
1. Run `synapse search <query>` before modifying code
2. Run `synapse graph <file>` before refactoring
3. Run `synapse ask "<error>" --think` on errors

**Detailed Rules**: See `.agent/rules.md`

---

**Detailed Rules**: See `.agent/rules.md`

---

## 🔑 Golden Prompt

When handing this project to an AI, use the following as the first message (System Prompt).
It automatically detects the language and enforces the appropriate rules.

```text
You are controlled by the Synapse AI Protocol.

1. If I speak KOREAN:
   - Read `docs/AI_RULES_KO.md` immediately.
   - Prove you followed the 'Pre-Work' instructions in that file.

2. If I speak ENGLISH (or other languages):
   - Read `docs/AI_RULES_EN.md` immediately.
   - Prove you followed the 'Pre-Work' instructions in that file.

🚫 DO NOT answer my question until you have completed steps 1 & 2.
```

---

*Synapse v0.1.0 | *Powered by Synapse & Antigravity*
