from tree_sitter import Language, Parser
import tree_sitter_python as tspython
from tracer import tracer

# Initialisation du parser
PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)

def get_code_structure(code_content: str) -> str:
    """
    Parse le code Python et extrait la hiérarchie des classes et fonctions via AST.
    """
    with tracer.start_as_current_span("analyze_ast_structure"):
        tree = parser.parse(bytes(code_content, "utf8"))
        
        def walk(node):
            structure = {
                "classes": [],
                "functions": [],
                "calls": []
            }
            
            if node.type == 'class_definition':
                name_node = node.child_by_field_name('name')
                if name_node:
                    structure["classes"].append(name_node.text.decode('utf8'))
            elif node.type == 'function_definition':
                name_node = node.child_by_field_name('name')
                if name_node:
                    structure["functions"].append(name_node.text.decode('utf8'))
            elif node.type == 'call':
                func_node = node.child_by_field_name('function')
                if func_node:
                    structure["calls"].append(func_node.text.decode('utf8'))
            
            for child in node.children:
                child_struct = walk(child)
                structure["classes"].extend(child_struct["classes"])
                structure["functions"].extend(child_struct["functions"])
                structure["calls"].extend(child_struct["calls"])
                
            return structure
            
        res = walk(tree.root_node)
        
        output = []
        if res["classes"]:
            output.append(f"Classes: {', '.join(res['classes'])}")
        if res["functions"]:
            output.append(f"Functions: {', '.join(res['functions'])}")
        if res["calls"]:
            output.append(f"Internal Calls: {', '.join(set(res['calls']))}")
            
        return "\n".join(output) if output else "Aucune structure identifiée."
