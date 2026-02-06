# 🤝 Contributing to Synapse

So you want to fix my messy code? Thank you. You are a hero.

## 🛠️ Development Setup

### 1. Clone & Install
```bash
git clone https://github.com/YuanArchive/synapse-ai-context.git
cd synapse-ai-context

# Create virtual env (Recommended)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install in edit mode
pip install -e .
pip install pytest pytest-cov
```

### 2. Run Tests
Before submitting a PR, please make sure you didn't break anything (more than it already is).
```bash
pytest tests/
```

---

## 🧠 Code Style & Rules

1. **Python 3.12+**: Utilizing modern features.
2. **Type Hints**: Mandatory. No `Any` unless absolutely necessary.
3. **Keep it Simple**: If I can't understand it, I can't merge it.
4. **English Comments**: Docstrings and comments should be in English (for global contributors).

---

## 🐛 Bug Reports

Please include:
- `synapse analyze . --verbose` output
- What you expected vs what happened
- "It doesn't work" is NOT a bug report.

## 💡 Feature Requests

If you want a new feature, please explain **why** it saves tokens or improves AI context.
Token efficiency is our #1 priority.

---

**Thank you for your help!** 🙏
