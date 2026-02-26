"""
KursarScript Compiler - Compiles KSPL code to an executable dictionary format.
"""
import re
from typing import Dict, List, Any


class KSPLCompileError(Exception):
    """Raised for syntax/structural errors during KSPL compilation."""


class KSPLCompiler:
    """
    Compiles KursarScript source code to an intermediate executable format.

    The output of :meth:`compile` is a dictionary that can be passed to the
    interpreter's internal structures or inspected for tooling purposes.
    """

    def __init__(self):
        self.classes: Dict = {}
        self.symbol_table: Dict = {}
        self.current_scope = "global"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def compile(self, source: str) -> Dict[str, Any]:
        """Compile KSPL *source* to executable format."""
        tokens = self.tokenize(source)
        tree = self.parse(tokens)
        return self.generate_code(tree)

    def optimize(self, executable: Dict[str, Any]) -> Dict[str, Any]:
        """Apply basic optimisations (currently a no-op placeholder)."""
        # TODO: constant folding, dead-code elimination, method inlining
        return executable.copy()

    # ------------------------------------------------------------------
    # Tokeniser
    # ------------------------------------------------------------------

    def tokenize(self, source: str) -> List[Dict]:
        tokens: List[Dict] = []
        lines = source.split('\n')
        line_num = 0

        for line in lines:
            line_num += 1
            line = line.strip()
            if not line or line.startswith('//'):
                continue

            # Class definition
            m = re.match(r'^class\s+(\w+)\s*\{', line)
            if m:
                tokens.append({'type': 'CLASS_DEF', 'value': m.group(1), 'line': line_num})
                continue

            # Function definition
            m = re.match(r'^fn\s+(\w+)\s*\(([^)]*)\)\s*\{', line)
            if m:
                params = [p.strip() for p in m.group(2).split(',') if p.strip()]
                tokens.append({'type': 'FN_DEF', 'value': m.group(1),
                               'params': params, 'line': line_num})
                continue

            # Field definition
            m = re.match(r'^field\s+(\w+)\s*=\s*(.*)', line)
            if m:
                tokens.append({'type': 'FIELD_DEF', 'value': m.group(1),
                               'expr': m.group(2), 'line': line_num})
                continue

            # Variable declaration
            m = re.match(r'^let\s+(\w+)\s*=\s*(.*)', line)
            if m:
                tokens.append({'type': 'LET_DEF', 'value': m.group(1),
                               'expr': m.group(2), 'line': line_num})
                continue

            # Return statement
            m = re.match(r'^return\s+(.*)', line)
            if m:
                tokens.append({'type': 'RETURN', 'expr': m.group(1), 'line': line_num})
                continue

            # If statement
            m = re.match(r'^if\s+(.+?)\s*\{', line)
            if m:
                tokens.append({'type': 'IF_STMT', 'condition': m.group(1), 'line': line_num})
                continue

            # Else statement
            if re.match(r'^\}\s*else\s*\{|^else\s*\{', line):
                tokens.append({'type': 'ELSE_STMT', 'line': line_num})
                continue

            # Closing brace
            if line == '}':
                tokens.append({'type': 'BRACE_CLOSE', 'line': line_num})
                continue

            # Assignment (not equality check)
            m = re.match(r'^([\w\.]+)\s*=\s*(.*)', line)
            if m and '==' not in line:
                tokens.append({'type': 'ASSIGNMENT', 'target': m.group(1),
                               'expr': m.group(2), 'line': line_num})
                continue

            # Expression / statement
            if '(' in line and line.endswith(')'):
                tokens.append({'type': 'EXPRESSION', 'value': line, 'line': line_num})
            else:
                tokens.append({'type': 'STATEMENT', 'value': line, 'line': line_num})

        return tokens

    # ------------------------------------------------------------------
    # Parser → AST dict
    # ------------------------------------------------------------------

    def parse(self, tokens: List[Dict]) -> Dict[str, Any]:
        tree: Dict[str, Any] = {
            'classes': {},
            'global_code': [],
            'imports': [],
        }

        i = 0
        current_class = None
        current_method = None

        while i < len(tokens):
            tok = tokens[i]
            t = tok['type']

            if t == 'CLASS_DEF':
                class_name = tok['value']
                current_class = {
                    'name': class_name,
                    'methods': {},
                    'fields': {},
                    'line': tok['line'],
                }
                tree['classes'][class_name] = current_class
                current_method = None

            elif t == 'FN_DEF' and current_class:
                method_name = tok['value']
                current_method = {
                    'name': method_name,
                    'params': tok['params'],
                    'body': [],
                    'line': tok['line'],
                }
                current_class['methods'][method_name] = current_method

            elif t == 'FIELD_DEF' and current_class:
                current_class['fields'][tok['value']] = {
                    'expr': tok['expr'],
                    'line': tok['line'],
                }

            elif t in ('LET_DEF', 'ASSIGNMENT', 'EXPRESSION', 'STATEMENT'):
                target = current_method if current_method else tree['global_code'] if not current_class else None
                if isinstance(target, dict):
                    target['body'].append(tok)
                elif isinstance(target, list):
                    target.append(tok)

            elif t == 'RETURN':
                if current_method:
                    current_method['body'].append(tok)
                else:
                    raise KSPLCompileError(f"Line {tok['line']}: return outside of method")

            elif t == 'IF_STMT':
                if_node = {
                    'type': 'IF',
                    'condition': tok['condition'],
                    'then_branch': [],
                    'else_branch': [],
                    'line': tok['line'],
                }
                i += 1
                while i < len(tokens) and tokens[i]['type'] not in ('ELSE_STMT', 'BRACE_CLOSE'):
                    if_node['then_branch'].append(tokens[i])
                    i += 1
                if i < len(tokens) and tokens[i]['type'] == 'ELSE_STMT':
                    i += 1
                    while i < len(tokens) and tokens[i]['type'] != 'BRACE_CLOSE':
                        if_node['else_branch'].append(tokens[i])
                        i += 1

                if current_method:
                    current_method['body'].append(if_node)
                else:
                    tree['global_code'].append(if_node)

            elif t == 'BRACE_CLOSE':
                # Close method scope first, then class scope
                if current_method:
                    current_method = None
                elif current_class:
                    current_class = None

            i += 1

        return tree

    # ------------------------------------------------------------------
    # Code generation
    # ------------------------------------------------------------------

    def generate_code(self, tree: Dict[str, Any]) -> Dict[str, Any]:
        executable: Dict[str, Any] = {
            'classes': {},
            'global_instructions': [],
            'metadata': {
                'version': '1.0',
                'compiler': 'KSPL Compiler',
            },
        }

        # Compile classes
        for class_name, class_info in tree['classes'].items():
            exec_class: Dict = {
                'name': class_name,
                'methods': {},
                'fields': class_info['fields'],
                'constructor': None,
            }
            for method_name, method_info in class_info['methods'].items():
                exec_method: Dict = {
                    'params': method_info['params'],
                    'instructions': [],
                }
                for stmt in method_info['body']:
                    instr = self._stmt_to_instruction(stmt)
                    if instr:
                        exec_method['instructions'].append(instr)

                exec_class['methods'][method_name] = exec_method
                if method_name == 'init':
                    exec_class['constructor'] = exec_method

            executable['classes'][class_name] = exec_class

        # Compile global code
        for stmt in tree['global_code']:
            instr = self._stmt_to_instruction(stmt, global_scope=True)
            if instr:
                executable['global_instructions'].append(instr)

        return executable

    def _stmt_to_instruction(self, stmt: Dict,
                              global_scope: bool = False) -> Dict:
        suffix = '_GLOBAL' if global_scope else ''
        t = stmt.get('type')

        if t == 'LET_DEF':
            return {'op': f'STORE{suffix}', 'target': stmt['value'],
                    'expr': stmt['expr']}
        if t == 'ASSIGNMENT':
            return {'op': f'ASSIGN{suffix}', 'target': stmt['target'],
                    'expr': stmt['expr']}
        if t == 'RETURN':
            return {'op': 'RETURN', 'expr': stmt['expr']}
        if t == 'EXPRESSION':
            return {'op': f'EXEC{suffix}', 'expr': stmt['value']}
        if t == 'STATEMENT':
            return {'op': f'EXEC{suffix}', 'expr': stmt.get('value', '')}
        if t == 'IF':
            return {
                'op': 'IF',
                'condition': stmt['condition'],
                'then': [self._stmt_to_instruction(s) for s in stmt['then_branch']],
                'else': [self._stmt_to_instruction(s) for s in stmt['else_branch']],
            }
        return {}
