import nbformat

def notebook_to_markdown(ipynb_bytes: bytes) -> str:
    """
    Converts a raw Jupyter Notebook file (bytes) into a standardized Markdown string.
    - Markdown cells -> Text
    - Code cells -> Fenced Code Blocks (```python ... ```)
    """
    try:
        # Decode bytes to string, then parse as Notebook Node
        nb_text = ipynb_bytes.decode('utf-8')
        nb = nbformat.reads(nb_text, as_version=4)
    except Exception as e:
        print(f"Error parsing notebook: {e}")
        return ""

    md_output = []

    for cell in nb.cells:
        if cell.cell_type == 'markdown':
            md_output.append(cell.source)
        elif cell.cell_type == 'code':
            # Preserve code exactly as is, wrapped in fences
            code_block = f"```python\n{cell.source}\n```"
            md_output.append(code_block)
    
    # Join with double newlines to ensure paragraph separation
    return "\n\n".join(md_output)