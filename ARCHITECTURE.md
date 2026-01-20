# DocForge Architecture

DocForge is a local-first, multi-agent engine designed to enforce **Document-Driven Development (DDD)**. It shifts documentation from a downstream "cleanup task" to an upstream "design authority."

## 1. High-Level Design (The "Shift-Left" Engine)

The system operates on a simple principle: **Code and Documentation must share a mathematical parity.**

Instead of using fuzzy semantic search (RAG) alone, DocForge uses **Tree-sitter** to extract a deterministic "Abstract Syntax Tree" (AST) from the code. It compares this AST against the requirements in the Product Requirements Document (PRD).

### Core Components
* **The Sovereign Fact Store (IR):** A JSON-based intermediate representation that normalizes Code (Functions/Classes) and Docs (Requirements) into a single schema.
* **The Logic Swarm:** A LangGraph state machine that orchestrates three agents:
    * **Interface Architect:** Fetches the facts.
    * **Google Stylist:** Generates drafts using the Google Developer Style Guide.
    * **Compliance Critic:** An adversarial agent that audits drafts for hallucinations and passive voice.
* **The Guardrail:** A Git Pre-Commit hook that blocks any code merge if the documentation drift score > 0.

## 2. The Logic Swarm (Agentic Workflow)

The system uses a cyclic graph (LangGraph) to refine documentation iteratively.

```mermaid
graph TD
    A[Code Change Detected] --> B(Parse AST);
    B --> C{Drift Detected?};
    C -- Yes --> D[Stylist Agent];
    D --> E[Draft Generation];
    E --> F[Compliance Critic];
    F -- Approved --> G[Commit Allowed];
    F -- Rejected --> D;