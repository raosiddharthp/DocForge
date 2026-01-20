import re

class SafeChunker:
    """
    Splits Markdown text into atomic chunks based on headers.
    Ensures no chunk exceeds a safety limit to prevent LLM freeze.
    """
    
    def __init__(self, max_tokens=1500):
        # Approx 1 token ~= 4 chars. 1500 tokens is safe for 8GB RAM.
        self.max_tokens = max_tokens

    def chunk_file(self, content: str):
        """
        Generator that yields chunks of text (Header + Content).
        """
        # 1. Regex to split by Headers (## Title)
        # Matches start of line, 1-6 hashes, space, then title
        # We capture the delimiter so we keep the header with the body
        pattern = r'(^#{1,6}\s+.+)'
        
        # Split preserves delimiters because of capturing group ()
        parts = re.split(pattern, content, flags=re.MULTILINE)
        
        # parts[0] is usually preamble/intro text before the first header
        if parts[0].strip():
            yield {"type": "preamble", "content": parts[0].strip()}

        # 2. Iterate through the rest (Header + Body pairs)
        # re.split returns [preamble, header1, body1, header2, body2...]
        for i in range(1, len(parts), 2):
            header = parts[i].strip()
            body = parts[i+1] if i+1 < len(parts) else ""
            
            full_chunk = f"{header}\n{body}"
            
            # 3. Safety Check: If chunk is massive, force split it
            if self._estimate_tokens(full_chunk) > self.max_tokens:
                # Fallback: Yield smaller pieces of the body
                yield from self._force_split(full_chunk)
            else:
                yield {"type": "section", "content": full_chunk.strip()}

    def _estimate_tokens(self, text):
        """Simple heuristic: 4 chars ~= 1 token"""
        return len(text) / 4

    def _force_split(self, text):
        """
        Emergency fallback for massive sections.
        Splits by paragraph.
        """
        paragraphs = text.split('\n\n')
        buffer = ""
        
        for p in paragraphs:
            if self._estimate_tokens(buffer) + self._estimate_tokens(p) < self.max_tokens:
                buffer += p + "\n\n"
            else:
                yield {"type": "fragment", "content": buffer.strip()}
                buffer = p + "\n\n"
        
        if buffer.strip():
            yield {"type": "fragment", "content": buffer.strip()}

# --- VERIFICATION BLOCK ---
if __name__ == "__main__":
    # Create a dummy massive markdown file in memory
    dummy_md = """
# Legacy System Documentation
This is the old intro.

## 1. Authentication
The system uses cookies. (Short section)

## 2. Massive Data Dump
""" + ("This is a very long line of repeated text to test the token limit safety mechanism.\n" * 500)

    print("✂️  Testing Safe Chunker...")
    chunker = SafeChunker(max_tokens=500) # Low limit to trigger force split
    
    count = 0
    for chunk in chunker.chunk_file(dummy_md):
        count += 1
        print(f"   [Chunk {count}] Type: {chunk['type']} | Length: {len(chunk['content'])} chars")
    
    print("✅ Chunker test complete.")