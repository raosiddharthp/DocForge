from typing import List, Dict, Optional
from pydantic import BaseModel
from src.db.schema import CodeEntity, DocEntity

class DriftReport(BaseModel):
    """The output of a drift analysis session."""
    entity_pairs: List[Dict] = []  # { "doc": DocEntity, "code": CodeEntity, "confidence": float }
    orphaned_docs: List[DocEntity] = [] # Requirements with no code
    orphaned_code: List[CodeEntity] = [] # Code with no requirements
    drift_score: float = 0.0 # 0.0 (Perfect) to 1.0 (Chaos)

class DriftAnalyzer:
    def analyze(self, code_facts: List[CodeEntity], doc_facts: List[DocEntity]) -> DriftReport:
        report = DriftReport()
        
        # 1. Naive Keyword Matching Strategy (The "MVP Heuristic")
        # In Phase 3, we replace this with Vector Search (RAG)
        
        matched_code_ids = set()
        matched_doc_ids = set()

        for doc in doc_facts:
            best_match = None
            
            # IMPROVED: Normalize Doc Title and Code Name
            # "Create User" -> "create user"
            # "create_user" -> "create user"
            doc_normalized = doc.section_title.lower().replace("_", " ")
            
            for code in code_facts:
                func_name_clean = code.name.lower().replace("_", " ")
                
                # Check if the clean function name appears in the Doc Title
                if func_name_clean in doc_normalized:
                    best_match = code
                    break
            
            if best_match:
                report.entity_pairs.append({
                    "doc_title": doc.section_title,
                    "code_name": best_match.name,
                    "status": "linked"
                })
                matched_code_ids.add(best_match.name) # Using name as ID for MVP
                matched_doc_ids.add(doc.section_title)
            else:
                # If it's a "MUST" requirement and we can't find code, that's Critical Drift.
                if doc.importance == 'must':
                    report.orphaned_docs.append(doc)

        # 2. Identify "Ghost Code" (Code that exists but isn't documented)
        for code in code_facts:
            if code.name not in matched_code_ids:
                report.orphaned_code.append(code)

        # 3. Calculate Drift Score
        # Simple formula: (Orphaned Docs + Orphaned Code) / Total Entities
        total_entities = len(code_facts) + len(doc_facts)
        if total_entities > 0:
            drift_count = len(report.orphaned_docs) + len(report.orphaned_code)
            report.drift_score = round(drift_count / total_entities, 2)

        return report

# Self-Test
if __name__ == "__main__":
    from src.db.schema import SourceMetadata

    # Mock Data
    meta = SourceMetadata(source_file="test", source_type="code", line_number=1)
    
    # Code: Only has 'login'
    code_sample = [
        CodeEntity(name="login", entity_type="func", signature="def login()", metadata=meta)
    ]
    
    # Docs: Has 'Login' (match) and 'Logout' (missing)
    doc_sample = [
        DocEntity(section_title="User Login", content_block="System must login.", importance="must", metadata=meta),
        DocEntity(section_title="User Logout", content_block="System must logout.", importance="must", metadata=meta)
    ]

    analyzer = DriftAnalyzer()
    result = analyzer.analyze(code_sample, doc_sample)
    
    print(f"Drift Score: {result.drift_score} (Lower is better)")
    print(f"Linked: {len(result.entity_pairs)}")
    print(f"Missing Code for Requirements: {[d.section_title for d in result.orphaned_docs]}")
    print(f"Undocumented Code: {[c.name for c in result.orphaned_code]}")