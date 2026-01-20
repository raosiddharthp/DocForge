import os

def create_structure():
    # The Architecture Map
    structure = [
        "src/core",          # LangGraph orchestration & Main Logic
        "src/agents",        # The Logic Swarm (Stylist, Critic, Architect)
        "src/parsing",       # Tree-sitter & Markdown AST parsers
        "src/db",            # Canonical Fact Store & Vector Interfaces
        "src/utils",         # Helper functions
        "config",            # Configuration files
        "tests/golden_set",  # Benchmarking data
        "data/inputs",       # PRDs and Source Code (Local Only)
        "data/vectors",      # FAISS/Chroma Indices (Local Only)
        "data/logs"          # System logs
    ]

    files = [
        "config/settings.yaml",
        "README.md",
        "requirements.txt",
        ".gitignore",
        "src/main.py"
    ]

    print("🏗️  Initializing DocForge Structure...")

    # Create Directories
    for folder in structure:
        os.makedirs(folder, exist_ok=True)
        # Create __init__.py in src subdirectories to make them packages
        if folder.startswith("src"):
            with open(os.path.join(folder, "__init__.py"), 'w') as f:
                pass
        print(f"   Created: {folder}/")

    # Create Files
    for file in files:
        if not os.path.exists(file):
            with open(file, 'w') as f:
                f.write("")
            print(f"   Created: {file}")

    print("\n✅ DocForge Skeleton Ready.")

if __name__ == "__main__":
    create_structure()