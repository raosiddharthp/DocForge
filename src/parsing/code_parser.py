import os
import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Node
from src.db.schema import CodeEntity, SourceMetadata

class CodeParser:
    def __init__(self):
        # Initialize Tree-sitter for Python
        # using the installed tree-sitter-python bindings
        self.LANGUAGE = Language(tspython.language())
        self.parser = Parser(self.LANGUAGE)

    def parse_file(self, file_path: str) -> list[CodeEntity]:
        """Reads a file and returns a list of CodeEntities."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, "rb") as f:
            source_bytes = f.read()

        tree = self.parser.parse(source_bytes)
        entities = []

        # Manual Traversal: Robust across tree-sitter versions
        def traverse(node: Node):
            if node.type == 'function_definition':
                entity = self._extract_function_info(node, source_bytes, file_path)
                entities.append(entity)
            
            # Recurse deeply
            for child in node.children:
                traverse(child)

        traverse(tree.root_node)
        return entities

    def _extract_function_info(self, node: Node, source: bytes, file_path: str) -> CodeEntity:
        # 1. Name
        name_node = node.child_by_field_name('name')
        func_name = "unknown"
        if name_node:
            func_name = source[name_node.start_byte : name_node.end_byte].decode('utf8')

        # 2. Parameters
        params_node = node.child_by_field_name('parameters')
        params_dict = {}
        if params_node:
            raw_params = source[params_node.start_byte : params_node.end_byte].decode('utf8')
            params_dict["raw"] = raw_params

        # 3. Return Type
        return_node = node.child_by_field_name('return_type')
        return_type = "None"
        if return_node:
            return_type = source[return_node.start_byte : return_node.end_byte].decode('utf8')

        # 4. Docstring
        docstring = None
        body_node = node.child_by_field_name('body')
        if body_node:
            for child in body_node.children:
                if child.type == 'expression_statement':
                    first_expr = child.children[0]
                    if first_expr.type == 'string':
                        docstring = source[first_expr.start_byte : first_expr.end_byte].decode('utf8')
                        docstring = docstring.strip('"""').strip("'''").strip()
                        break

        # 5. Build Metadata
        meta = SourceMetadata(
            source_file=file_path,
            source_type='code',
            line_number=node.start_point[0] + 1
        )

        return CodeEntity(
            name=func_name,
            entity_type='function',
            signature=f"def {func_name}{params_dict.get('raw', '()')} -> {return_type}",
            docstring=docstring,
            parameters=params_dict,
            return_type=return_type,
            metadata=meta
        )

# Self-Test
if __name__ == "__main__":
    dummy_code = """
def authenticate(user: str, retries: int = 3) -> bool:
    "Attempts to login the user."
    return True
    """
    with open("temp_test.py", "w") as f:
        f.write(dummy_code)

    try:
        parser = CodeParser()
        results = parser.parse_file("temp_test.py")
        import json
        print(json.dumps([r.model_dump() for r in results], indent=2, default=str))
    finally:
        if os.path.exists("temp_test.py"):
            os.remove("temp_test.py")