from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal
from datetime import datetime

# --- 1. The Atomic "Fact" (Source of Truth) ---
class SourceMetadata(BaseModel):
    """Where did this fact come from?"""
    source_file: str       # e.g., "auth_spec.md" or "auth_service.py"
    source_type: Literal['code', 'documentation']
    line_number: Optional[int] = None
    commit_hash: Optional[str] = None  # For version tracking
    last_updated: datetime = Field(default_factory=datetime.now)

# --- 2. The Code Entity (What we built) ---
class CodeEntity(BaseModel):
    """Represents a function, class, or API endpoint extracted from source."""
    name: str              # e.g., "login_user"
    entity_type: str       # "function", "class", "endpoint"
    signature: str         # e.g., "def login_user(email: str, password: str) -> bool"
    docstring: Optional[str] = None
    parameters: Dict[str, str] = Field(default_factory=dict) # {"email": "str"}
    return_type: Optional[str] = None
    metadata: SourceMetadata

# --- 3. The Documentation Entity (What we designed) ---
class DocEntity(BaseModel):
    """Represents a requirement or claim found in a PRD/Spec."""
    section_title: str     # e.g., "3.1 User Authentication"
    content_block: str     # The actual text paragraph
    importance: Literal['must', 'should', 'could'] = 'must' # RFC 2119 levels
    associated_code_ref: Optional[str] = None # Inferred link to code (e.g., "login_user")
    metadata: SourceMetadata

# --- 4. The Canonical Fact Store (The Sovereign State) ---
class FactStore(BaseModel):
    """The complete 'Brain' of the project."""
    project_name: str
    code_facts: List[CodeEntity] = Field(default_factory=list)
    doc_facts: List[DocEntity] = Field(default_factory=list)
    
    # The Drift Report will live here later
    drift_logs: List[Dict] = Field(default_factory=list)