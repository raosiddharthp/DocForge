import os
import re
from typing import List, Tuple
from src.db.schema import DocEntity, SourceMetadata

class DocParser:
    """
    Parses Markdown files into atomic 'DocEntity' chunks based on headers.
    Also acts as the 'Ambiguity Critic' by flagging vague verbs.
    """
    
    # Words that indicate "Technical Debt Hiding"
    AMBIGUOUS_VERBS = {
        "streamline", "optimize", "facilitate", "leverage", "robust", 
        "seamless", "cutting-edge", "state-of-the-art"
    }

    # RFC 2119 Keywords for importance
    IMPORTANCE_MAP = {
        "must": "must", "required": "must", "shall": "must",
        "should": "should", "recommended": "should",
        "may": "could", "optional": "could"
    }

    def parse_file(self, file_path: str) -> List[DocEntity]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        entities = []
        
        # Split by Headers (## Header)
        # We capture the header title and the content following it
        # Regex: matches ^#{1,6} [space] Title ... content
        sections = re.split(r'(^#{1,6}\s+.+)', content, flags=re.MULTILINE)
        
        # The split includes the delimiter (header) in the list, so we pair them up
        # sections[0] is usually preamble before the first header
        if sections[0].strip():
             entities.append(self._create_entity("Preamble", sections[0], file_path, 1))

        for i in range(1, len(sections), 2):
            header = sections[i].strip().lstrip('#').strip()
            body = sections[i+1] if i+1 < len(sections) else ""
            
            if not body.strip():
                continue

            entity = self._create_entity(header, body, file_path, i)
            entities.append(entity)

        return entities

    def _create_entity(self, title: str, content: str, path: str, index: int) -> DocEntity:
        # 1. Detect Importance (RFC 2119)
        lower_content = content.lower()
        importance = "could" # Default
        for key, val in self.IMPORTANCE_MAP.items():
            if f" {key} " in lower_content:
                importance = val
                break
        
        # 2. Ambiguity Detection (The "Google Bar" check)
        ambiguities = [word for word in self.AMBIGUOUS_VERBS if word in lower_content]
        
        # If ambiguous, we prepend a warning note to the content for the Agent to see
        final_content = content.strip()
        if ambiguities:
            warning = f"\n[AMBIGUITY WARNING]: The following vague terms were found: {', '.join(ambiguities)}. Proceed with caution."
            final_content += warning

        # 3. Create Metadata
        meta = SourceMetadata(
            source_file=path,
            source_type='documentation',
            line_number=index # Approx index, since regex split loses exact lines
        )

        return DocEntity(
            section_title=title,
            content_block=final_content,
            importance=importance,
            metadata=meta
        )

# Self-Test
if __name__ == "__main__":
    dummy_md = """
# User Authentication
The system MUST provide a secure login endpoint.
It should streamline the user experience using robust JWT tokens.

## Password Policy
Passwords should be at least 8 characters.
    """
    with open("temp_test.md", "w") as f:
        f.write(dummy_md)

    try:
        parser = DocParser()
        results = parser.parse_file("temp_test.md")
        import json
        print(json.dumps([r.model_dump() for r in results], indent=2, default=str))
    finally:
        if os.path.exists("temp_test.md"):
            os.remove("temp_test.md")