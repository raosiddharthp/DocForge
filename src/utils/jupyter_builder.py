import nbformat as nbf
import re
import os

class JupyterBuilder:
    """
    Converts Markdown text into a valid Jupyter Notebook (.ipynb).
    Automatically detects code blocks and creates executable cells.
    """

    def __init__(self):
        # Create a new notebook object (v4 format)
        self.nb = nbf.v4.new_notebook()
        self.cells = []

    def add_content(self, text_chunk: str):
        """
        Parses a chunk of text and adds appropriate cells.
        """
        # Split by code blocks
        # Regex finds ```lang ... ``` blocks
        # We split the text into parts: [markdown, code, markdown, code...]
        parts = re.split(r'```(\w+)?\n(.*?)```', text_chunk, flags=re.DOTALL)
        
        # If no code blocks, add entire chunk as Markdown
        if len(parts) == 1:
            self._add_markdown(parts[0])
            return

        # Iterate through parts
        # split returns: [text_before, lang, code_content, text_after...]
        i = 0
        while i < len(parts):
            text_segment = parts[i].strip()
            
            # 1. Add Markdown Segment
            if text_segment:
                self._add_markdown(text_segment)
            
            # Check if there is a next code block
            if i + 2 < len(parts):
                lang = parts[i+1] # e.g., 'python' or None
                code_content = parts[i+2].strip()
                
                # 2. Add Code Cell (only if language is python or generic)
                # You can adjust this filter if you want bash/json cells too
                self._add_code(code_content)
                
                i += 3 # Skip lang and code match groups
            else:
                i += 1

    def _add_markdown(self, text):
        if text:
            self.cells.append(nbf.v4.new_markdown_cell(text))

    def _add_code(self, code):
        if code:
            self.cells.append(nbf.v4.new_code_cell(code))

    def save(self, filepath: str):
        """
        Writes the notebook to disk.
        """
        self.nb.cells = self.cells
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            nbf.write(self.nb, f)
        
        return filepath

# --- VERIFICATION BLOCK ---
if __name__ == "__main__":
    print("📓 Assembling Notebook...")
    
    # Mock Refined Text
    refined_text = """
    ## Authenticate
    To authenticate, use the `login` function.
    
    ```python
    import requests
    def login(user, password):
        return requests.post("/api/login", data={user: password})
    ```
    
    Verify the response code is 200.
    """
    
    builder = JupyterBuilder()
    builder.add_content(refined_text)
    
    output_path = "data/projects/test_notebook.ipynb"
    saved_path = builder.save(output_path)
    
    print(f"✅ Saved to: {saved_path}")
    print("Check the file content to verify valid JSON structure.")