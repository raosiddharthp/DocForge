# DocForge ⚒️

**The Shift-Left Documentation Engine.**

DocForge is an open-source, local-first tool that keeps your documentation and code in perfect sync. It uses a multi-agent AI swarm to write, audit, and enforce documentation standards *before* you commit code.

## 🚀 Features

* **Zero-Trust Auditing:** The "Compliance Critic" agent rejects drafts that hallucinate parameters or use passive voice.
* **Google Style Guide:** Enforces the "Google Developer Documentation Style Guide" automatically.
* **Local-First:** Runs 100% offline using **Ollama** and **Llama-3**. Your IP never leaves your machine.
* **Git Guardrails:** A pre-commit hook blocks merges if documentation drift is detected.
* **Writer Dashboard:** A visual UI to monitor drift and generate docs interactively.

## 🛠️ Installation

### Prerequisites
1.  **Python 3.10+**
2.  **Ollama** (Running locally)

### Quick Start
Run these commands to set up the environment and install the Git Guardrails:

```bash
# 1. Clone & Enter
git clone [https://github.com/your-username/docforge.git](https://github.com/your-username/docforge.git)
cd docforge

# 2. Install Dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Pull the Local Model
ollama pull llama3

# 4. Install the Guardrail (Git Hook)
# Copy and paste this block to create the hook locally:
cat << 'EOF' > .git/hooks/pre-commit
#!/bin/bash
echo "🛡️  DocForge Guardrail Active..."
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep "\.py$")
[ -z "$STAGED_FILES" ] && exit 0

PASS=true
for FILE in $STAGED_FILES; do
    echo "🔍 Auditing $FILE..."
    if ! python3 -m src.main "$FILE"; then
        PASS=false
    fi
done

if [ "$PASS" = "true" ]; then
    exit 0
else
    echo "⛔ DocForge Audit Failed. Commit blocked."
    exit 1
fi
EOF

# 5. Make it executable
chmod +x .git/hooks/pre-commit