# Contributing to DocForge

We welcome contributions! DocForge follows a **Local-First, Zero-Trust** philosophy.

## Development Setup

1.  **Fork & Clone** the repository.
2.  **Install Dependencies:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```
3.  **Local LLM:** Ensure you have [Ollama](https://ollama.com) running with `llama3`.

## The Rules

### 1. Zero Freeze Policy
* **No Parallel Inference:** Agents must run serially to respect consumer hardware RAM.
* **Token Limits:** Use `SafeChunker` for large files. Do not feed raw files > 2000 tokens to the Agents.

### 2. Architecture Constraints
* **No Cloud Calls:** Do not add API calls to OpenAI/Anthropic. DocForge must remain air-gapped.
* **Data Sovereignty:** Never modify `.gitignore` to allow `data/` files to be committed.

### 3. Testing
Before submitting a PR, verify the Logic Swarm:
```bash
# Run the "Green Test" parity check
python3 -m src.main tests/golden_set/test_api.py --spec tests/golden_set/test_spec.md